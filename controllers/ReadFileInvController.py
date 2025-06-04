import re
from utils.constants import ValidateFile, Pattern, Columns
from models.ReadFileInvModel import ReadFileInvModel

class ReadFileInvController:
    '''
    Controller: xử lý các vấn đề liên quan đến FILE
    Model: xử lý các vấn đề liên quan đến DỮ LIỆU
    '''
    def __init__(self):
        self.model = ReadFileInvModel()

    def validate_file(self, uploaded_files):
        if (len(uploaded_files) == 0):
            return False, "No file uploaded"
        elif len(uploaded_files) % 3 != 0:
            return False, f"The number of imported files must be divisible by 3. Total files {len(uploaded_files)}"
            # st.toast('The number of files to import must be 3 (EO-FG-RPM).',  icon="⚠️")
        for file in uploaded_files:
            if Pattern.DOT.value in file.name:
                duoifile = re.split(Pattern.DOT_PATTERN.value, file.name)[-1]
            else:
                duoifile = None
                
            if duoifile not in ValidateFile.LIST_DUOI_FILE_IMPORT.value:
                return False, f"Invalid file type for {file.name}"
        return True, "Valid file"
    
    def process_files(self, uploaded_files):
        '''Xử lý nhiều file'''
        results = {
            'success': [],
            'errors': [],
            'total_processed': 0
        }

        #Kiểm tra file
        is_valid, message = self.validate_file(uploaded_files)
        if not is_valid:
            results['errors'].append({'error': message})
        else:
            #Gọi method models
            processed_data  = self.model.process_data(uploaded_files)
            results['combined_data'] = processed_data
            results['success'].append(f'Import Inventory Successfully. Total rows {processed_data.shape[0]:,}')
        
        return results