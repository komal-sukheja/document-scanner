# 📄 Smart Document Scanner

A professional web-based document scanner application that automatically detects, transforms, and exports document images as clean scanned copies. Built with Streamlit and OpenCV for real-time document processing.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **🔍 Automatic Document Detection**: Intelligent edge detection and contour approximation to find document boundaries
- **📐 Perspective Correction**: Four-point perspective transformation for accurate document alignment
- **🎨 Multiple Scan Modes**: 
  - Black & White mode for clean text documents
  - Enhanced B&W mode for documents with backgrounds
- **🧹 Noise Reduction**: Adjustable morphological operations to remove artifacts
- **📤 Multi-Format Export**: Download as JPG, PNG, or PDF
- **🎯 Real-time Preview**: Instant visualization of corner detection and processing results
- **💻 Responsive UI**: Clean, intuitive interface with sidebar controls

## 🚀 Demo

[Live Demo on Streamlit Cloud](https://your-app-url.streamlit.app) *(Update with your deployment URL)*

## 📸 Screenshots

### Original Document Detection
The app automatically detects document boundaries with corner markers:

### Scanned Output
Clean, professionally scanned document with perspective correction:

## 🛠️ Technology Stack

- **Frontend Framework**: [Streamlit](https://streamlit.io/)
- **Image Processing**: [OpenCV](https://opencv.org/)
- **Image Manipulation**: [Pillow (PIL)](https://python-pillow.org/)
- **Numerical Computing**: [NumPy](https://numpy.org/)

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/document-scanner.git
cd document-scanner
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv scanenv
scanenv\Scripts\activate

# macOS/Linux
python3 -m venv scanenv
source scanenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Running Locally

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Basic Workflow

1. **Upload Document**: Click "Upload Document Image" and select a photo of your document
2. **Auto-Detection**: The app automatically detects document boundaries (marked with green corners)
3. **Adjust Settings** (Optional):
   - Choose scan mode: **Black & White** or **Enhanced B&W**
   - Adjust noise reduction (0-5) for cleaner output
4. **Export**: Click "Export Document" and download in your preferred format (JPG/PNG/PDF)
5. **Reset**: Use the reset button if detection needs to be re-run

### Tips for Best Results

- 📷 Ensure good lighting when capturing document photos
- 🖼️ Make sure all four corners of the document are visible
- 📐 Place document on a contrasting background
- 🎯 Use **Black & White** mode for text-heavy documents
- 🌈 Use **Enhanced B&W** mode for documents with colored backgrounds
- 🧹 Increase noise reduction for images with artifacts or grain

## 📦 Project Structure

```
document-scanner/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
└── .streamlit/           # Streamlit configuration (optional)
    └── config.toml
```

## 🧩 Core Components

### Image Processing Pipeline

1. **Edge Detection**: Canny edge detection with Gaussian blur preprocessing
2. **Contour Detection**: Identifies the largest 4-sided contour as document boundary
3. **Perspective Transform**: Four-point transformation for bird's-eye view
4. **Scan Processing**: Adaptive thresholding with optional noise reduction
5. **Export**: Multi-format conversion (JPG, PNG, PDF)

### Key Functions

- `detect_document_contour()`: Automated document boundary detection
- `four_point_transform()`: Perspective correction algorithm
- `apply_scan_mode()`: Applies different scanning filters
- `apply_noise_reduction()`: Morphological operations for cleaner output

## ⚙️ Configuration

The app uses the following default parameters (adjustable in `app.py`):

```python
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 200
GAUSSIAN_BLUR = (5, 5)
CONTOUR_APPROX_FACTOR = 0.02
```

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository and branch
6. Set main file path: `app.py`
7. Click "Deploy"

Your app will be live at `https://your-app-name.streamlit.app`

### Deploy to Other Platforms

The app can also be deployed to:
- **Heroku**: Add `setup.sh` and `Procfile`
- **Railway**: Direct deployment from GitHub
- **AWS/GCP/Azure**: Using containerization with Docker

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues & Limitations

- Very low-light or blurry images may fail detection
- Documents with complex backgrounds may require manual corner adjustment
- PDF export is single-page only
- Maximum file upload size depends on Streamlit Cloud limits (200MB default)

## 📝 Future Enhancements

- [ ] Manual corner adjustment with drag-and-drop
- [ ] Batch processing for multiple documents
- [ ] OCR integration for text extraction
- [ ] Document type classification
- [ ] Cloud storage integration
- [ ] Mobile app version

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- OpenCV community for excellent documentation
- Streamlit team for the amazing framework
- Inspiration from mobile document scanning apps

## 📧 Contact

For questions or feedback, please open an issue or reach out at your.email@example.com

---

⭐ **If you find this project useful, please consider giving it a star!**