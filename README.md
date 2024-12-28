
# PDF Merger for Canvas Files

A Python script to collect, organize, and merge files from Canvas classes/modules into a singular PDF file.

## Features
- Fetch lecture notes dynamically from Canvas.
- Merge all notes into a single PDF for easy access.
- Configurable through environment variables for reusability.

## Requirements
- Python 3.8+
- Canvas API access
- Environment variables properly set

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/notes-synthesizer.git
   cd notes-synthesizer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure `.env`:
   ```plaintext
   API_URL=https://your-canvas-api-url
   API_KEY=your-canvas-api-key
   COURSE_ID=your-course-id
   INSTITUTION_URL=https://your-institution-url
   NOTE_FOLDER_DIRECTORY=/path/to/your/notes
   COMBINED_NOTES_DIRECTORY=/path/to/output/combined-notes.pdf
   SENDER_EMAIL=your-email@example.com
   RECEIVER_EMAIL=receiver-email@example.com
   EMAIL_PASSWORD=your-email-password
   MODULE_ITEM_IDS=[]
   ```

4. Run the script:
   ```bash
   python notes_synthesizer_dynamic.py
   ```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
