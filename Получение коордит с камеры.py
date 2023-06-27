import cv2
import numpy as np
import time
import os
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk

def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def on_button_click():
    selected_port = port_dropdown.get()
    global com 
    com = selected_port
    print(com)
    root.destroy()

root = tk.Tk()
root.title("Порт")

# Получаем размер экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Рассчитываем координаты для центрирования окна
x = (screen_width / 2) - (200 / 2)
y = (screen_height / 2) - (80 / 2)

# Устанавливаем размер и положение окна
root.geometry('%dx%d+%d+%d' % (200, 80, x, y))

port_label = tk.Label(root, text="Выберетите порт :")
port_label.pack()

available_ports = get_available_ports()
port_dropdown = tk.ttk.Combobox(root, values=available_ports)
port_dropdown.pack()

button = tk.Button(root, text="Подключить", command=on_button_click)
button.pack()

root.bind('<Return>', on_button_click)

root.mainloop()

# Получаем доступ к USB камере
cap = cv2.VideoCapture(0)

# Создаем окно с заданными размерами
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('frame', 1280, 960)

# Устанавливаем параметры порта
try:
    ser = serial.Serial(com, 9600, timeout=1)
except:
    ser = 0
# ser.open()
n=0

while True:
    # Считываем кадр с USB камеры
    ret, frame = cap.read()

    # Преобразуем кадр в пространство цветов HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Определяем диапазон красного цвета в HSV
    lower_red = np.array([0, 128, 128])
    upper_red = np.array([5, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([175, 50, 50])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)

    # Объединяем две маски для красного цвета
    mask = cv2.bitwise_or(mask1, mask2)

    # Определяем диапазон желтого цвета в HSV
    lower_yellow = np.array([23, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask3 = cv2.inRange(hsv, lower_yellow, upper_yellow)

    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask4 = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Объединяем две маски для красного цвета
    maskY = cv2.bitwise_or(mask3, mask4)

    # Находим контуры объектов на маске
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contoursY, hierarchyY = cv2.findContours(maskY, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Если контуры присутствуют на кадре
    

    #     # Находим координаты центра контура
    #     M = cv2.moments(max_contour)
    #     if M['m00'] != 0:
    #         cx = int(M['m10'] / M['m00'])
    #         cy = int(M['m01'] / M['m00'])

    #         # Рисуем круг вокруг красного объекта
    #         cv2.circle(frame, (cx, cy), 20, (0, 0, 255), 2)

    #         # Очищаем терминал
    #         os.system('cls' if os.name == 'nt' else 'clear')

    #         # Выводим координаты центра круга в терминал
    #         print("Центр координат красный: ({}, {})".format(cx, cy))

    #         # Добавляем текст с координатами центра
    #         text = "({}, {})".format(cx, cy)
    #         cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv2.LINE_AA)

    #         if n == 5 and ser != 0:
    #             # Отправляем координаты на Arduino
    #             ser.write(str.encode("{}, {}\n".format(cx, cy)))
    #             n = 0

    # Если контуры присутствуют на кадре

    #     # Находим координаты центра контура
    #     M = cv2.moments(max_contour)
    #     if M['m00'] != 0:
    #         cx = int(M['m10'] / M['m00'])
    #         cy = int(M['m01'] / M['m00'])

    #         # Рисуем круг вокруг красного объекта
    #         cv2.circle(frame, (cx, cy), 20, (60, 255, 255), 2)

    #         # Очищаем терминал
    #         os.system('cls' if os.name == 'nt' else 'clear')

    #         # Выводим координаты центра круга в терминал
    #         print("Центр координат желтый: ({}, {})".format(cx, cy))

    #         # Добавляем текст с координатами центра
    #         text = "({}, {})".format(cx, cy)
    #         cv2.putText(frame, text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1, cv2.LINE_AA)

    #         if n == 5 and ser != 0:
    #             # Отправляем координаты на Arduino
    #             ser.write(str.encode("{}, {}\n".format(cx, cy)))
    #             n = 0

    # Находим координаты центра контура
    
    if contoursY and contours:
        # Находим самый большой контур (самый крупный красный объект)
        max_contourY = max(contoursY, key=cv2.contourArea)
        MY = cv2.moments(max_contourY)

        max_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(max_contour)        

        if M['m00'] != 0 and MY['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cxY = int(MY['m10'] / MY['m00'])
            cyY = int(MY['m01'] / MY['m00'])

            # Рисуем круг вокруг красного объекта
            cv2.circle(frame, (cx, cy), 20, (0, 0, 255), 2)
            cv2.circle(frame, (cxY, cyY), 20, (60, 255, 255), 2)

            # Очищаем терминал
            os.system('cls' if os.name == 'nt' else 'clear')

            # Выводим координаты центра круга в терминал
            print("Центр координат красный: ({}, {})".format(cx, cy))
            print("Центр координат желтый: ({}, {})".format(cxY, cyY))

            # Добавляем текст с координатами центра
            # text = "({}, {})".format(cx, cy)
            # cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv2.LINE_AA)

            # textY = "({}, {})".format(cxY, cyY)
            # cv2.putText(frame, textY, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1, cv2.LINE_AA)

            # Вычисляем расстояние между центрами
            distance = np.sqrt((cx - cxY)**2 + (cy - cyY)**2)
            print("Расстояние между центрами: {}".format(distance))

            textY = "({}, {})".format("Ras", distance)
            cv2.putText(frame, textY, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1, cv2.LINE_AA)

            if n == 15 and ser != 0:
                # Отправляем координаты на Arduino
                ser.write(str.encode("{}\n".format(distance)))
                n = 0


    # Отображаем кадр с выделенным красным объектом
    cv2.imshow('frame', frame)

    # Добавляем задержку в 1 секунду
    # time.sleep(1)

    # Если нажата клавиша '1', выходим из цикла
    if cv2.waitKey(1) & 0xFF == ord('1') or cv2.waitKey(1) & 0xFF == ord('1'):
        break
    
    n+=1

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()
if ser !=0:
    ser.close()