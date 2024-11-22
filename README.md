# ThunderData: Advanced Text Processing Toolkit

A comprehensive data engineering application with advanced natural language processing capabilities to transform and analyze text data efficiently. Built with React frontend and FastAPI backend.

## 🚀 Features

### Text Processing Capabilities
- **Tokenization**: Split text into individual tokens
- **Stopword Removal**: Remove common stopwords from text
- **Lemmatization**: Convert words to their base/dictionary form
- **Text Vectorization**: Convert text to numerical vectors (TF-IDF and Count Vectorization)
- **Named Entity Recognition**: Extract named entities (e.g., Person, Organization, Location)
- **Part of Speech Tagging**: Identify grammatical parts of speech
- **Stemming**: Reduce words to their root/stem form

### Technical Features
- **Real-time Processing Status**: Track file processing progress with detailed status updates
- **Batch Processing**: Handle large datasets efficiently with configurable batch sizes
- **Flexible Input/Output**: Support for multiple file formats (CSV, JSON, TXT, XLSX)
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Validation**: Input validation with file type and size constraints
- **Asynchronous Processing**: Background task processing for large files
- **RESTful API**: Well-documented API endpoints for all operations

## 🛠️ Project Structure

```
ThunderData/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── processor.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── processing.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── status.py
│   │   │   └── validation.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── processed/
│   ├── uploads/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.js
│   │   │   ├── ProcessingStatus.js
│   │   │   └── TransformationConfig.js
│   │   ├── utils/
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── README.md
└── README.md
```

## 🔧 Technical Requirements

### Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Pandas
- NumPy
- SpaCy (with en_core_web_sm model)
- scikit-learn
- NLTK

### Frontend
- Node.js 16+
- React 18+
- Axios for API calls
- Material-UI for components

## 🚦 API Endpoints

- `POST /api/upload`: Upload file for processing
- `POST /api/process/{file_id}`: Process file with specified transformations
- `GET /api/status/{file_id}`: Get processing status
- `GET /api/download/{filename}`: Download processed file

## 💻 Development Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/ThunderData.git
cd ThunderData
```

2. Set up backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Set up frontend
```bash
cd frontend
npm install
npm start
```

## 🔒 Validation Constraints

- Supported file types: .csv, .json, .txt, .xlsx
- Maximum file size: 100MB
- Batch processing with configurable batch size
- Strict transformation type and parameter validation

## 🌟 Future Improvements

- Support for more language models
- Enhanced vectorization techniques
- More advanced NLP transformations
- Improved frontend configuration UI
- Real-time text analysis
- Custom transformation pipeline builder
- Export configurations for reproducibility
- Parallel processing for large datasets

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
