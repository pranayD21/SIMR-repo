from io import BytesIO
from pdfminer.high_level import extract_pages
from langchain_community.tools import BaseTool
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar, LTPage


# Transcript processing langchain custom tool
class TranscriptParser(BaseTool):
    name: str = "TranscriptParser"
    # name = "TranscriptParser"
    description: str = "A tool to extract text from PDF transcripts in a buffer and return the data as a JSON object."

    def extract_text_from_line(self, layout_obj):
        line_content = ""
        if isinstance(layout_obj, LTTextLine):
            for text_content_obj in layout_obj:
                line_content += text_content_obj.get_text()
        return line_content.strip()

    def parse_transcript(self, layout_obj):
        rows = []
        if isinstance(layout_obj, LTPage):
            for child in layout_obj:
                rows.extend(self.parse_transcript(child))
        elif isinstance(layout_obj, LTTextBox):
            current_row = []
            for text_line in layout_obj:
                line_text = self.extract_text_from_line(text_line)
                if line_text:
                    current_row.append(line_text)
            if current_row:
                rows.append({"type": "row", "text": current_row})
        return rows

    def extract_transcript_from_pdf_buffer(self, buffer: BytesIO):
        transcript_data = {"transcript_elements": []}
        for page_layout in extract_pages(buffer, laparams=LAParams()):
            transcript_data["transcript_elements"].extend(self.parse_transcript(page_layout))
        return transcript_data

    def _run(self, pdf_buffer: BytesIO) -> dict:
        """
        Run the tool with the provided PDF buffer.
        """
        return self.extract_transcript_from_pdf_buffer(pdf_buffer)