# Setting up Gemma LLM with Flask on Raspberry Pi

This guide will help you set up a Flask server on your Raspberry Pi that uses the Gemma LLM model via MediaPipe Tasks to generate child-friendly responses.

## Prerequisites

- Raspberry Pi 4 (with at least 4GB RAM recommended) running Raspberry Pi OS
- Internet connection for downloading packages and the model
- Python 3.7 or newer

## Installation Steps

1. **Update your Raspberry Pi**:

   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Install required system packages**:

   ```bash
   sudo apt install -y python3-pip python3-venv
   ```

3. **Create a project directory and virtual environment**:

   ```bash
   mkdir -p ~/gemma-flask/models
   cd ~/gemma-flask
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python packages**:

   ```bash
   pip install --upgrade pip
   pip install flask mediapipe
   ```

5. **Download the Model**

   To use the model, you must first download it from one of the following sources:

   [Hugging Face Hub](https://huggingface.co/google/gemma-3n-E2B-it-litert-preview)

   [Google Drive](https://drive.google.com/file/d/1JKFt9RB6EDwQm_RZ0aWcYo81g6C8jdTT/view?usp=sharing)

6. **Save the Python script**:
   Save the provided `app.py` script in your project directory:

   ```bash
   cd ~/gemma-flask
   # Create app.py using the code provided in the other artifact
   ```

7. **Run the application**:
   ```bash
   export MODEL_PATH="$HOME/gemma-flask/models/gemma-3n-E2B-it-litert-preview.task"
   python app.py
   ```

## Testing the API

1. **Check if the server is running**:

   ```bash
   curl http://localhost:5000/health
   ```

   Expected response:

   ```json
   {
     "mediapipe_available": true,
     "model_loaded": true,
     "model_path": "/home/pi/gemma-flask/models/gemma-3n-E2B-it-litert-preview.task",
     "status": "healthy"
   }
   ```

2. **Make a text generation request**:
   ```bash
   curl -X POST http://localhost:5000/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt":"Explain how rainbows work"}'
   ```

## Running as a Service

To make the application start automatically on boot:

1. **Create a systemd service file**:

   ```bash
   sudo nano /etc/systemd/system/gemma-flask.service
   ```

2. **Add the following content**:

   ```
   [Unit]
   Description=Gemma Flask API Service
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/gemma-flask
   Environment="PATH=/home/pi/gemma-flask/venv/bin"
   Environment="MODEL_PATH=/home/pi/gemma-flask/models/gemma-3n-E2B-it-litert-preview.task"
   ExecStart=/home/pi/gemma-flask/venv/bin/python /home/pi/gemma-flask/app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service**:

   ```bash
   sudo systemctl enable gemma-flask
   sudo systemctl start gemma-flask
   ```

4. **Check the service status**:
   ```bash
   sudo systemctl status gemma-flask
   ```

## Troubleshooting

- **Model not loading**: Check that the model file exists at the specified path and is in the correct MediaPipe Tasks format
- **MediaPipe import errors**: Ensure you're using a compatible version of MediaPipe for your Raspberry Pi architecture
- **Memory issues**: If the model is too large for your Raspberry Pi's memory, consider using a smaller model or increasing swap space

## Note

#### The train_10M.zip file is supposed to be used for fine-tuning the model however the Gemma model does not support fine-tuning at the moment. You can use it for other purposes or ignore it.

## Credits

This guide is based on the MediaPipe Tasks documentation and the Gemma LLM model from Google. For more information, refer to the [MediaPipe Tasks documentation](https://google.github.io/mediapipe/tasks/python/overview.html) and the [Gemma model page](https://huggingface.co/google/gemma-3n-E2B-it-litert-preview).

The fine tune dataset is gotten https://babylm.github.io/ from the BabyLM project, which provides a dataset for training language models on child-friendly text.
