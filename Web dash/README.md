# 🏥 IoT and AI-Based Health Monitoring System

A comprehensive health monitoring system that combines IoT sensors, AI analysis, and real-time web dashboard for continuous health monitoring.

## 🌟 Features

- **Real-time Vital Signs Monitoring**
  - ECG monitoring using AD8232 sensor
  - Body temperature tracking with LM35 sensor
  - Pulse rate monitoring
  - Live data visualization

- **AI-Powered Analysis**
  - ECG abnormality detection using TensorFlow
  - LangChain + Groq LLM integration for health reports
  - Comprehensive health analysis and recommendations

- **Interactive Dashboard**
  - Real-time vital signs display
  - ECG graph visualization
  - Patient history tracking
  - AI-generated health reports
  - Data export capabilities

## 🛠️ Technology Stack

- **Backend**
  - FastAPI (Python web framework)
  - TensorFlow (AI/ML)
  - LangChain + Groq (LLM integration)
  - Supabase (Database)

- **Frontend**
  - HTML5/CSS3
  - Bootstrap 5
  - Chart.js
  - JavaScript

- **Hardware**
  - Arduino
  - AD8232 ECG Sensor
  - LM35 Temperature Sensor
  - Pulse Rate Sensor

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Arduino IDE
- Required Python packages (see requirements.txt)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/health-monitoring-dashboard.git
cd health-monitoring-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
GROQ_API_KEY=your_groq_api_key
```

4. Run the application:
```bash
uvicorn main:app --reload
```

## 📊 Dashboard Features

1. **Live Vitals Overview**
   - Real-time display of vital signs
   - Device ID tracking
   - Timestamp monitoring

2. **ECG Graph**
   - Real-time ECG visualization
   - 30-second rolling window
   - Raw and smoothed view options

3. **Patient History**
   - Historical data tracking
   - Search functionality
   - CSV export capability

4. **AI Report Generator**
   - Comprehensive health analysis
   - Vital signs interpretation
   - Health recommendations
   - Professional medical formatting

## 🤝 Project Team

- **Aarish Quazi** - Project Leader
- **Aaditya Kaushik** - AI & Backend Developer
- **Anshuman Singh Sikarwar** - Cloud Integration
- **Ashmit Kumar Kurmi** - Hardware & Sensors

## 📝 About

This project was developed at Swami Keshvanand Institute of Technology (SKIT), Jaipur, as part of an initiative to bridge the gap between remote healthcare monitoring and clinical practices. The system aims to provide real-time health monitoring and analysis, enabling healthcare providers to make informed decisions and take timely actions.

## 🔒 Security

- Environment variables for sensitive data
- Secure API key management
- Protected data transmission
- Regular security updates

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Swami Keshvanand Institute of Technology
- Project Mentors
- Open Source Community
- Contributing Developers 