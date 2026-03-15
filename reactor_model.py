import random

def reactor_step(temp, flux, coolant):

    # dao động nhẹ
    temp += random.uniform(-1, 1)

    flux += random.uniform(-5, 5)

    coolant += random.uniform(-2, 2)

    # coolant ảnh hưởng nhiệt độ
    temp += (500 - coolant) * 0.01

    # pressure phụ thuộc temp
    pressure = 15 + (temp - 300) * 0.02

    # radiation phụ thuộc flux
    radiation = 50 + (flux - 1000) * 0.01

    if random.random() < 0.01:
        coolant -= 80 # 1% nước làm mát bị vấn đề

    if random.random() < 0.01:
        temp += 80 # 1% nhiệt độ tăng đột biến

    temp += random.uniform(-1, 1)
    # cố cân bằng về 300 độ
    temp += (300 - temp) * 0.08

    return temp, pressure, flux, coolant, radiation