import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

device = torch.device('cpu')

def load_phobert_model():
    """
    Load PhoBERT model và tokenizer
    """
    try:
        model_name = "vinai/phobert-base"
        print(f"Đang download PhoBERT model: {model_name}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("Đã load tokenizer thành công!")
        
        # Load model
        model = AutoModel.from_pretrained(model_name)
        print("Đã load model thành công!")
        
        # Đặt model về chế độ evaluation và chuyển về CPU
        model = model.to(device)
        model.eval()
        
        # Kiểm tra xem model có hoạt động không
        test_text = "test"
        test_inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True, max_length=10)
        test_inputs = {k: v.to(device) for k, v in test_inputs.items()}
        with torch.no_grad():
            test_outputs = model(**test_inputs)
        
        print("Đã test model thành công!")
        print("Đã load thành công PhoBERT model!")
        return model, tokenizer
        
    except Exception as e:
        print(f"Lỗi khi load PhoBERT model: {e}")
        print("Hãy kiểm tra kết nối internet và thử lại")
        print("Nếu vẫn lỗi, hãy thử:")
        print("1. Kiểm tra kết nối internet")
        print("2. Xóa thư mục ~/.cache/huggingface/ và thử lại")
        print("3. Kiểm tra phiên bản transformers và torch")
        raise e

def get_text_embedding(text, model, tokenizer, max_length=512):
    """
    Lấy embedding cho text sử dụng PhoBERT
    """
    if not text or text.strip() == "":
        # Trả về vector 0 nếu text rỗng
        return np.zeros(768)
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        # Chuyển inputs về device (CPU)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Lấy embedding của [CLS] token
        embedding_tensor = outputs.last_hidden_state[0, 0, :]
        embedding_tensor = embedding_tensor.detach().cpu()
        
        # Kiểm tra xem tensor có phải là float32 không, nếu không thì chuyển đổi
        if embedding_tensor.dtype != torch.float32:
            embedding_tensor = embedding_tensor.float()
        
        # Chuyển đổi sang numpy array
        embedding = embedding_tensor.numpy()
        
        # Đảm bảo kết quả là 1D array với 768 chiều
        if embedding.ndim > 1:
            embedding = embedding.flatten()
        
        # Kiểm tra độ dài
        if len(embedding) != 768:
            print(f"Warning: Embedding length {len(embedding)} != 768 for text '{text[:50]}...'")
            # Nếu độ dài không đúng, pad hoặc truncate
            if len(embedding) < 768:
                embedding = np.pad(embedding, (0, 768 - len(embedding)), 'constant')
            else:
                embedding = embedding[:768]
        
        return embedding
    except Exception as e:
        print(f"Lỗi khi xử lý text '{text}': {e}")
        # Trả về vector 0 nếu có lỗi
        return np.zeros(768)
