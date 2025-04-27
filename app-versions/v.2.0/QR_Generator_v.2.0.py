import qrcode
from reportlab.lib.pagesizes import landscape, inch
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, red, white
import os
from tkinter import *
from tkinter import filedialog, messagebox

# Изначально установите параметры для первого варианта
QR_SIZE = 17 * mm
PADDING = 5 * mm
BACKGROUND_WIDTH = 20 * mm
BACKGROUND_HEIGHT = 20 * mm
QR_COLOR = black
TEXT_COLOR = red
FONT_SIZE = 9
FONT_NAME = "Helvetica-Bold"
QR_COLUMNS = 19
QR_ROWS = 10
PAGE_WIDTH = 500 * mm
PAGE_HEIGHT = 260 * mm
CORNER_RADIUS = 1.5 * mm
COORD_QR = 0.8 * mm
COORD_NUM = 1.1 * mm

def create_qr_pdf(filename, start_number, end_number):
    c = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    current_number = start_number
    while current_number <= end_number:
        # Расчет начальных координат для размещения QR кодов
        x_start = (PAGE_WIDTH - (QR_COLUMNS * BACKGROUND_WIDTH + (QR_COLUMNS - 1) * PADDING)) / 2
        y_start = (PAGE_HEIGHT - (QR_ROWS * BACKGROUND_HEIGHT + (QR_ROWS - 1) * PADDING)) / 2

        for row in range(QR_ROWS):
            for col in range(QR_COLUMNS):
                if current_number > end_number:
                    break

                # Координаты для текущего QR кода
                x = x_start + col * (BACKGROUND_WIDTH + PADDING)
                y = y_start + (QR_ROWS - row - 1) * (BACKGROUND_HEIGHT + PADDING)

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(
                    f"https://app.akku-batt.rent/scooters?number={current_number:04d}")
                qr.make(fit=True)

                # Рисование подложки с закругленными углами
                c.setStrokeColor(red)
                c.setFillColor(white)
                c.roundRect(x, y, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, radius=CORNER_RADIUS, fill=1, stroke=1)

                # Рисование QR кода
                img = qr.make_image(fill_color="black", back_color="white")
                img_path = f"qr_{current_number:04d}.png"  # Форматирование номера с ведущими нулями
                img.save(img_path)
                c.drawImage(img_path, x + (BACKGROUND_WIDTH - QR_SIZE) / 2, y + (BACKGROUND_HEIGHT - QR_SIZE) / COORD_QR,
                            width=QR_SIZE, height=QR_SIZE)
                os.remove(img_path)

                # Рисование номера самоката
                c.setFillColor(TEXT_COLOR)
                c.setFont(FONT_NAME, FONT_SIZE)
                text = f"{current_number:04d}"
                text_width = c.stringWidth(text, FONT_NAME, FONT_SIZE)
                c.drawString(x + (BACKGROUND_WIDTH - text_width) / 2, y + COORD_NUM, text)

                current_number += 1

            if current_number > end_number:
                break

        if current_number <= end_number:
            c.showPage()

    c.save()


def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)


def update_qr_parameters():
    global QR_SIZE, PADDING, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, COORD_QR, COORD_NUM, QR_COLUMNS, QR_ROWS, FONT_SIZE
    global PAGE_WIDTH, PAGE_HEIGHT

    if size_var.get() == "Квадрат 2.0 см":
        QR_SIZE = 13 * mm
        BACKGROUND_WIDTH = 20 * mm
        BACKGROUND_HEIGHT = 20 * mm
        COORD_QR = 1.1 * mm
        COORD_NUM = 1 * mm
        QR_COLUMNS = 19
        QR_ROWS = 10
        FONT_SIZE = 5
    elif size_var.get() == "Квадрат 2.6 см":
        QR_SIZE = 17 * mm
        BACKGROUND_WIDTH = 26 * mm
        BACKGROUND_HEIGHT = 26 * mm
        COORD_QR = 0.75 * mm
        COORD_NUM = 1.6 * mm
        QR_COLUMNS = 15
        QR_ROWS = 8
        FONT_SIZE = 9



def generate_qr_codes():
    try:
        start_num = int(start_entry.get())
        end_num = int(end_entry.get())
        folder = folder_path.get()
        pdf_name = pdf_name_entry.get()

        if not folder or not pdf_name:
            messagebox.showwarning("Внимание", "Папка и название файла не могут быть пустыми.")
            return

        filename = os.path.join(folder, f"{pdf_name}.pdf")
        create_qr_pdf(filename, start_num, end_num)
        messagebox.showinfo("Успех", f"PDF файл '{pdf_name}.pdf' успешно создан в '{folder}'!")

    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числа для диапазона.")


root = Tk()
root.title("Генератор QR кодов")
root.geometry("400x450")

Label(root, text="Выберите размер квадрата:").pack(pady=5)

size_var = StringVar(value="Квадрат 2.0 см")
size_menu = OptionMenu(root, size_var, "Квадрат 2.0 см", "Квадрат 2.6 см", command=lambda _: update_qr_parameters())
size_menu.pack(pady=5)

Label(root, text="Начальный номер:").pack(pady=5)
start_entry = Entry(root)
start_entry.pack(pady=5)

Label(root, text="Конечный номер:").pack(pady=5)
end_entry = Entry(root)
end_entry.pack(pady=5)

Label(root, text="Папка для сохранения:").pack(pady=5)
folder_path = StringVar()
folder_entry = Entry(root, textvariable=folder_path)
folder_entry.pack(pady=5)

Button(root, text="Выбрать папку", command=select_folder).pack(pady=5)

Label(root, text="Название PDF файла:").pack(pady=5)
pdf_name_entry = Entry(root)
pdf_name_entry.pack(pady=5)

Button(root, text="Сгенерировать PDF", command=generate_qr_codes).pack(pady=20)

root.mainloop()
