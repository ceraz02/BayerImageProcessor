#include <opencv2/opencv.hpp>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <stdexcept>

void detect_and_fix_shift(const std::string &filename_in, const std::string &filename_out,
                          int width = 4096, int height = 4098, int patch = 8, int stride = 4096) {
    // ---- Load raw binary ----
    std::ifstream infile(filename_in, std::ios::binary);
    if (!infile) throw std::runtime_error("Cannot open input file");

    std::vector<uint8_t> raw(width * height);
    infile.read(reinterpret_cast<char*>(raw.data()), raw.size());
    infile.close();

    if (infile.gcount() != raw.size()) {
        throw std::runtime_error("File size does not match expected dimensions");
    }

    // Reshape into matrix (height x width)
    cv::Mat raw_img(height, width, CV_8UC1, raw.data());

    // ---- Step 1: Detect missing byte ----
    std::vector<double> scores;
    std::vector<int> positions;

    for (int row = 0; row < height - patch; row += patch) {
        for (int col = 0; col < width - patch; col += patch) {
            cv::Rect roi(col, row, patch, patch);
            cv::Mat crop = raw_img(roi);

            cv::Mat rgb;
            cv::cvtColor(crop, rgb, cv::COLOR_BayerRG2BGR); // equivalent to BayerRG2RGB

            // Compute mean R, G, B
            cv::Scalar mean_val = cv::mean(rgb);
            double mean_b = mean_val[0];
            double mean_g = mean_val[1];
            double mean_r = mean_val[2];

            double score = mean_g / (mean_r + mean_b + 1e-6);
            scores.push_back(score);
            positions.push_back(row * width + col);
        }
    }

    // Find biggest drop
    double max_diff = -1.0;
    int best_idx = 0;
    for (size_t i = 1; i < scores.size(); i++) {
        double diff = std::abs(scores[i] - scores[i - 1]);
        if (diff > max_diff) {
            max_diff = diff;
            best_idx = positions[i];
        }
    }

    std::cout << "Likely missing byte at global index " << best_idx
              << ", row=" << best_idx / width
              << ", col=" << best_idx % width << std::endl;

    // ---- Step 2: Fix shift ----
    std::vector<uint8_t> fixed(raw.size());
    std::copy(raw.begin(), raw.begin() + best_idx, fixed.begin());
    fixed[best_idx] = 0; // lost byte replaced with 0
    std::copy(raw.begin() + best_idx, raw.end() - 1, fixed.begin() + best_idx + 1);

    // Save corrected file
    std::ofstream outfile(filename_out, std::ios::binary);
    outfile.write(reinterpret_cast<char*>(fixed.data()), fixed.size());
    outfile.close();

    std::cout << "Corrected file written to " << filename_out << std::endl;
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " input.bin output.bin" << std::endl;
        return 1;
    }

    try {
        detect_and_fix_shift(argv[1], argv[2]);
    } catch (std::exception &e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
