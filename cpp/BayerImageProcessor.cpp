#include <opencv2/opencv.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <iomanip>

namespace fs = std::filesystem;

// Helper: format bytes as hex string
std::string bytesToHex(const std::vector<uint8_t>& data, size_t start, size_t len) {
    std::ostringstream oss;
    for (size_t i = 0; i < len; i++) {
        if (i > 0) oss << " ";
        oss << std::uppercase << std::setw(2) << std::setfill('0')
            << std::hex << (int)data[start + i];
    }
    return oss.str();
}

// Helper: format bytes as decimal string
std::string bytesToDec(const std::vector<uint8_t>& data, size_t start, size_t len) {
    std::ostringstream oss;
    for (size_t i = 0; i < len; i++) {
        if (i > 0) oss << " ";
        oss << std::dec << (int)data[start + i];
    }
    return oss.str();
}

// Write header/footer info
void writeHeaderFooter(std::ofstream& hf, const std::string& binPath, const cv::Mat& raw) {
    std::string base = fs::path(binPath).stem().string();
    std::string imgNb = base;
    auto pos = base.find_last_of('_');
    if (pos != std::string::npos) {
        imgNb = base.substr(pos + 1);
    }

    hf << "File: " << imgNb << "\n";

    // Extract header (first row, 11 bytes) and footer (last row, 66 bytes)
    std::vector<uint8_t> headerBytes(raw.cols);
    std::vector<uint8_t> footerBytes(raw.cols);
    memcpy(headerBytes.data(), raw.ptr(0), raw.cols);
    memcpy(footerBytes.data(), raw.ptr(raw.rows - 1), raw.cols);

    hf << "Header : " << bytesToHex(headerBytes, 0, 11) << "\n";
    hf << "         " << bytesToDec(headerBytes, 0, 11) << "\n";

    int analogGain = headerBytes[8];
    hf << "Analog Gain : 0x" << std::hex << analogGain
       << " (" << std::dec << analogGain << ")\n";

    int integrationTime = headerBytes[9] | (headerBytes[10] << 8);
    double integrationTimeMs = integrationTime * 0.0104;
    hf << "Integration Time : 0x"
       << std::hex << std::setw(4) << std::setfill('0') << integrationTime
       << " (" << std::dec << integrationTime << " = "
       << std::fixed << std::setprecision(3) << integrationTimeMs << " ms)\n";

    hf << "Footer : " << bytesToHex(footerBytes, 0, 66) << "\n";
    hf << "         " << bytesToDec(footerBytes, 0, 66) << "\n\n";
}

// Process one .bin file
void processBinFile(const std::string& binPath,
                    const std::string& outputDir,
                    const std::string& mode,
                    int compressionLevel,
                    bool writeHF,
                    std::ofstream& hf) {
    constexpr int rows = 4098;
    constexpr int cols = 4096;
    constexpr size_t expectedSize = rows * cols;

    // Read file
    std::ifstream fin(binPath, std::ios::binary);
    if (!fin) {
        std::cerr << "Error opening " << binPath << "\n";
        return;
    }
    std::vector<uint8_t> buffer((std::istreambuf_iterator<char>(fin)),
                                std::istreambuf_iterator<char>());
    fin.close();

    if (buffer.size() < expectedSize) {
        buffer.resize(expectedSize, 0);
    } else if (buffer.size() > expectedSize) {
        buffer.resize(expectedSize);
    }

    // Wrap into cv::Mat
    cv::Mat raw(rows, cols, CV_8UC1, buffer.data());
    cv::Mat rawImage = raw.rowRange(1, 4097).clone(); // remove first + last rows

    std::string base = fs::path(binPath).stem().string();

    // Write PNG(s)
    std::vector<int> compressionParams = {cv::IMWRITE_PNG_COMPRESSION, compressionLevel};
    if (mode == "normal" || mode == "both") {
        cv::imwrite((fs::path(outputDir) / (base + ".png")).string(), rawImage, compressionParams);
    }
    if (mode == "colorize" || mode == "both") {
        cv::Mat rgbImage;
        cv::cvtColor(rawImage, rgbImage, cv::COLOR_BayerRG2BGR);
        cv::imwrite((fs::path(outputDir) / (base + "_colorize.png")).string(), rgbImage, compressionParams);
    }

    // Write header/footer
    // if (writeHF) {
    //     std::ofstream outHF(fs::path(outputDir) / (base + "_header_footer.txt"));
    //     writeHeaderFooter(outHF, binPath, raw);
    // }
    if (writeHF) {
        if (hf.is_open()) {
            writeHeaderFooter(hf, binPath, raw);
        } else {
            std::ofstream outHF(fs::path(outputDir) / (base + "_header_footer.txt"));
            writeHeaderFooter(outHF, binPath, raw);
            outHF.close();
        }
    }

}

// Process a series of .bin files
void processSeries(const std::string& seriesName,
                   const std::vector<std::string>& inputs,
                   const std::string& outputDir,
                   const std::string& mode,
                   int compressionLevel,
                   bool writeHF) {
    std::vector<std::string> seriesFiles;

    for (auto& inp : inputs) {
        if (fs::is_directory(inp)) {
            for (auto& p : fs::directory_iterator(inp)) {
                if (p.path().extension() == ".bin" &&
                    p.path().filename().string().rfind(seriesName + "_", 0) == 0) {
                    seriesFiles.push_back(p.path().string());
                }
            }
        } else if (fs::path(inp).extension() == ".bin" &&
                   fs::path(inp).filename().string().rfind(seriesName + "_", 0) == 0) {
            seriesFiles.push_back(inp);
        }
    }

    if (seriesFiles.empty()) {
        std::cout << "No matching .bin files found for the given series name.\n";
        return;
    }

    fs::create_directories(outputDir);

    std::ofstream hf;
    if (writeHF) {
        hf.open(fs::path(outputDir) / (seriesName + "_header_footer.txt"));
    }

    int total = seriesFiles.size();
    for (int i = 0; i < total; i++) {
        std::cout << "Processing image " << (i + 1) << " of " << total
                  << ": " << fs::path(seriesFiles[i]).filename().string() << "\n";
        processBinFile(seriesFiles[i], outputDir, mode, compressionLevel, writeHF, hf);
    }

    if (hf.is_open()) hf.close();
}

void printUsage(const char* prog) {
    std::cout << "Usage: " << prog << " [options] inputs...\n"
              << "Options:\n"
              << "  -o <dir>     Output directory (default: .)\n"
              << "  -m <mode>    Mode: normal | colorize | both | none (default: colorize)\n"
              << "  -c <level>   PNG compression level [0-9] (default: 3)\n"
              << "  -hf          Extract header/footer info\n"
              << "  -s <series>  Series name for processing\n"
              << "  -h           Show this help\n";
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printUsage(argv[0]);
        return 1;
    }

    std::vector<std::string> inputs;
    std::string output = ".";
    std::string mode = "colorize";
    int compression = 3;
    bool headerfooter = false;
    std::string seriesName;

    // Parse args
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "-o" && i + 1 < argc) {
            output = argv[++i];
        } else if (arg == "-m" && i + 1 < argc) {
            mode = argv[++i];
        } else if (arg == "-c" && i + 1 < argc) {
            compression = std::stoi(argv[++i]);
            if (compression < 0) compression = 0;
            if (compression > 9) compression = 9;
        } else if (arg == "-hf") {
            headerfooter = true;
        } else if (arg == "-s" && i + 1 < argc) {
            seriesName = argv[++i];
        } else if (arg == "-h") {
            printUsage(argv[0]);
            return 0;
        } else {
            inputs.push_back(arg);
        }
    }

    if (inputs.empty()) {
        std::cerr << "No input files or directories specified.\n";
        return 1;
    }

    if (!seriesName.empty()) {
        processSeries(seriesName, inputs, output, mode, compression, headerfooter);
    } else {
        std::vector<std::string> binFiles;
        for (auto& inp : inputs) {
            if (fs::is_directory(inp)) {
                for (auto& p : fs::directory_iterator(inp)) {
                    if (p.path().extension() == ".bin")
                        binFiles.push_back(p.path().string());
                }
            } else if (fs::path(inp).extension() == ".bin") {
                binFiles.push_back(inp);
            }
        }

        if (binFiles.empty()) {
            std::cout << "No .bin files found.\n";
            return 1;
        }

        fs::create_directories(output);
        std::ofstream hf;

        int total = binFiles.size();
        for (int i = 0; i < total; i++) {
            std::cout << "Processing image " << (i + 1) << " of " << total
                      << ": " << fs::path(binFiles[i]).filename().string() << "\n";
            processBinFile(binFiles[i], output, mode, compression, headerfooter, hf);
        }
    }

    return 0;
}
