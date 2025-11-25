# Aetheria Beta

A professional 3D render analysis tool that helps architects and designers improve their visualizations through AI-powered feedback.

## Features

- 🎨 **Color Palette Analysis**: Extract and compare color palettes from renders and references
- 🔍 **Texture Detection**: Identify materials and get texture suggestions from Poly Haven
- 💡 **Lighting Analysis**: Get recommendations for exposure, contrast, and HDRI settings
- ⭐ **Realism Scoring**: Receive detailed critiques and scores for your renders
- 🚀 **AI Enhancement**: Upscale and enhance renders with automated processing

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Flask (Python)
- **Deployment**: Vercel (Frontend)

## Local Development

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rushit313/AetheriaBeta.git
   cd AetheriaBeta
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the development servers**

   Terminal 1 - Backend:
   ```bash
   cd backend
   venv\Scripts\activate
   python app.py
   ```

   Terminal 2 - Frontend:
   ```bash
   npm run dev
   ```

6. **Open the app**
   Navigate to `http://localhost:5173` in your browser

## Environment Variables

Create a `.env` file based on `.env.example`:

- `AETHERIA_PORT`: Backend API port (default: 5001)
- `VITE_API_URL`: Backend API URL for frontend

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Deployment

### Frontend (Vercel)

1. Push your code to GitHub
2. Import the repository in Vercel
3. Configure environment variables in Vercel dashboard
4. Deploy!

### Backend

The Flask backend needs separate hosting. Options:
- Render.com (recommended for free tier)
- Railway.app
- Heroku

## Project Structure

```
AetheriaBeta/
├── src/              # React frontend source
│   ├── App.jsx       # Main application component
│   ├── components/   # Reusable UI components
│   └── lib/          # Utilities and helpers
├── backend/          # Flask API server
│   ├── app.py        # Main backend application
│   └── requirements.txt
├── dist/             # Production build output
└── public/           # Static assets
```

## License

Proprietary - All rights reserved

## Contact

For questions or support, reach out via GitHub issues.
