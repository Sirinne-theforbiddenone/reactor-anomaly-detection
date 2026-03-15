# FILE NÀY LÀ MODEL AI PHÁT HIỆN BẤT THƯỜNG TRONG DATA
from sklearn.ensemble import IsolationForest

#khúc này thuần vibe code
class AnomalyDetector:

    def __init__(self): #hàm khởi tạo

        self.model = IsolationForest(contamination=0.02) #gen ra 1 đống dữ liệu random, trong đó có 2% là dell ổn

    def train(self, data): #hàm train model, data là mảng 2 chiều lấy dữ liệu từ cái database kia 

        self.model.fit(data) #model nhận biết chỗ data dell ổn kia

    def detect(self, x): #hàm detect, x là 1 mảng 1 chiều chứa dữ liệu mới cần kiểm tra

        result = self.model.predict([x]) #model sẽ trả về 1 mảng chứa 1 giá trị duy nhất, nếu là -1 thì bất thường, nếu là 1 thì bình thường

        return result[0] 