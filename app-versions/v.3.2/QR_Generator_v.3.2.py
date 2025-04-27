from tkinter import IntVar, filedialog, messagebox, StringVar
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton
from PIL import Image
import qrcode
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, red, white
import os

# Default
QR_COLUMNS_MAX = 10
NUMBER_OF_COLUMN_STEPS = 20

QR_ROWS_MAX = 8
NUMBER_OF_ROWS_STEPS = 8

QR_SIZE = 17 * mm
PADDING = 5 * mm

BACKGROUND_WIDTH = 20 * mm
BACKGROUND_HEIGHT = 20 * mm

QR_COLOR = black
TEXT_COLOR = red
FONT_SIZE = 9
FONT_NAME = "Helvetica-Bold"

PAGE_WIDTH = 500 * mm
PAGE_HEIGHT = 260 * mm
CORNER_RADIUS = 1.5 * mm
COORD_QR = 0.8 * mm
COORD_NUM = 1.1 * mm
DOP_QR = 0 * mm

QR_COLUMNS = 19
QR_ROWS = 10

def update_column_max(QRSizeVar):
    global QR_COLUMNS_MAX, NUMBER_OF_COLUMN_STEPS, QR_ROWS_MAX, NUMBER_OF_ROWS_STEPS, QR_SIZE
    global BACKGROUND_WIDTH, BACKGROUND_HEIGHT, COORD_QR, COORD_NUM, FONT_SIZE, DOP_QR
    qr_size_value = QRSizeVar.get()

    if qr_size_value == 20:
        QR_COLUMNS_MAX = 19
        NUMBER_OF_COLUMN_STEPS = 20

        NUMBER_OF_ROWS_STEPS = 10
        QR_ROWS_MAX = 10

        QR_SIZE = 17 * mm
        BACKGROUND_WIDTH = 20 * mm
        BACKGROUND_HEIGHT = 20 * mm

        COORD_QR = 0.6 * mm
        COORD_NUM = 0.9 * mm

        FONT_SIZE = 10
        DOP_QR = 15

    elif qr_size_value == 26:
        QR_COLUMNS_MAX = 15
        NUMBER_OF_COLUMN_STEPS = 20

        NUMBER_OF_ROWS_STEPS = 8
        QR_ROWS_MAX = 8

        QR_SIZE = 23 * mm
        BACKGROUND_WIDTH = 26 * mm
        BACKGROUND_HEIGHT = 26 * mm

        COORD_QR = 0.6 * mm
        COORD_NUM = 1.6 * mm

        FONT_SIZE = 12
        DOP_QR = 0

    update_column_slider()


def update_column_slider():
    ColumnSlider.configure(to=QR_COLUMNS_MAX)
    RowsSlider.configure(to=QR_ROWS_MAX)


def create_qr_pdf(filename, start_number, end_number):
    temp_folder = os.path.join(os.path.dirname(__file__), 'raw_qr_code')
    os.makedirs(temp_folder, exist_ok=True)

    c = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    current_number = start_number
    while current_number <= end_number:
        x_start = (PAGE_WIDTH - (QR_COLUMNS * BACKGROUND_WIDTH + (QR_COLUMNS - 1) * PADDING)) / 2
        y_start = (PAGE_HEIGHT - (QR_ROWS * BACKGROUND_HEIGHT + (QR_ROWS - 1) * PADDING)) / 2

        for row in range(QR_ROWS):
            for col in range(QR_COLUMNS):
                if current_number > end_number:
                    break

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

                c.setStrokeColor(red)
                c.setFillColor(white)
                c.roundRect(x, y, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, radius=CORNER_RADIUS, fill=1, stroke=1)

                img = qr.make_image(fill_color="black", back_color="white")
                img_path = os.path.join(temp_folder, f"qr_{current_number:04d}.png")
                img.save(img_path)
                c.drawImage(img_path, x + (BACKGROUND_WIDTH - QR_SIZE) / 2,
                            y + (BACKGROUND_HEIGHT - QR_SIZE + 4.3) / COORD_QR,
                            width=QR_SIZE, height=QR_SIZE)

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

def generate_qr_codes():
    try:
        start_num = int(RangeToQRFrom.get())
        end_num = int(RangeOfQRTo.get())
        folder = folder_path.get()
        pdf_name = NameOfPDFFile.get()

        if not folder or not pdf_name:
            messagebox.showwarning("Внимание", "Папка и название файла не могут быть пустыми.")
            return

        filename = os.path.join(folder, f"{pdf_name}.pdf")
        create_qr_pdf(filename, start_num, end_num)
        messagebox.showinfo("Успех", f"PDF файл '{pdf_name}.pdf' успешно создан в '{folder}'!")

    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числа для диапазона.")


QRCodeGenerator = ctk.CTk()
QRCodeGenerator.title("QR Code Generator by: 1ce0ne")
QRCodeGenerator.geometry("430x800+10+10")
QRCodeGenerator.resizable(False, False)
ctk.set_appearance_mode("dark")

RightFrame = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=6,
    fg_color="#333333",
    width=415,
    height=740)
RightFrame.place(x=7.5, y=30)

# Размер QR кодов
SizeOfQR = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
SizeOfQR.place(x=25, y=50)

QRSizeVar = IntVar()

SizeOfQrLabel = CTkLabel(master=SizeOfQR,
                         text_color="white",
                         font=("Arial", 16),
                         text='Размер QR кода')
SizeOfQrLabel.place(x=125, y=5)

SizeQrTwoZero = ctk.CTkRadioButton(
    SizeOfQR,
    variable=QRSizeVar,
    value=20,
    text="Квадрат 2.0 см",
    fg_color="#9600BB",
    text_color="white",
    hover_color="#444343",
    command=lambda: update_column_max(QRSizeVar))
SizeQrTwoZero.place(x=35, y=45)

SizeQrTwoSix = ctk.CTkRadioButton(
    SizeOfQR,
    variable=QRSizeVar,
    value=26,
    text="Квадрат 2.6 см",
    fg_color="#9600BB",
    text_color="white",
    hover_color="#444343",
    command=lambda: update_column_max(QRSizeVar))
SizeQrTwoSix.place(x=220, y=45)

# Диапазон QR кодов
RangeOfQR = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
RangeOfQR.place(x=25, y=150)

RangeOfQRLabel = CTkLabel(master=RangeOfQR,
                          text_color="white",
                          font=("Arial", 16),
                          text='Диапазон номеров QR кодов')
RangeOfQRLabel.place(x=80, y=5)

RangeOfQrFromLabel = CTkLabel(master=RangeOfQR,
                              text_color="white",
                              font=("Arial", 14),
                              text='От:')
RangeOfQrFromLabel.place(x=37, y=36)

RangeToQRFrom = CTkEntry(
    RangeOfQR,
    height=30,
    width=70,
    corner_radius=2)
RangeToQRFrom.place(x=67, y=37)

RangeToQrToLabel = CTkLabel(master=RangeOfQR,
                            text_color="white",
                            font=("Arial", 14),
                            text='До:')
RangeToQrToLabel.place(x=240, y=36)

RangeOfQRTo = CTkEntry(
    RangeOfQR,
    height=30,
    width=70,
    corner_radius=2)
RangeOfQRTo.place(x=270, y=37)

# Кол-во в столбец
ColumnQrOnList = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
ColumnQrOnList.place(x=25, y=250)

SliderColumnValueLabel = ctk.CTkLabel(ColumnQrOnList,
                                      text="Кол-во столбцов: 1",
                                      fg_color="#444343",
                                      text_color="white",
                                      font=("Arial", 16))
SliderColumnValueLabel.place(x=120, y=5)


def update_column_label(value):
    global QR_COLUMNS
    SliderColumnValueLabel.configure(text=f"Кол-во столбцов: {int(value)}")
    QR_COLUMNS = int(value)


ColumnSlider = ctk.CTkSlider(master=ColumnQrOnList,
                             from_=1,
                             to=QR_COLUMNS_MAX,
                             width=350,
                             number_of_steps=NUMBER_OF_COLUMN_STEPS,
                             button_color="purple",
                             progress_color="white",
                             orientation="horizontal",
                             command=update_column_label)
ColumnSlider.place(x=10, y=40)

# Кол-во в строку
RowsQrOnList = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
RowsQrOnList.place(x=25, y=350)

SliderRowsValueLabel = ctk.CTkLabel(RowsQrOnList,
                                    text="Кол-во строк: 1",
                                    fg_color="#444343",
                                    text_color="white",
                                    font=("Arial", 16))
SliderRowsValueLabel.place(x=130, y=5)


def update_rows_label(value):
    global QR_ROWS
    SliderRowsValueLabel.configure(text=f"Кол-во строк: {int(value)}")
    QR_ROWS = int(value)


RowsSlider = ctk.CTkSlider(master=RowsQrOnList,
                           from_=1,
                           to=QR_ROWS_MAX,
                           width=350,
                           number_of_steps=NUMBER_OF_ROWS_STEPS,
                           button_color="purple",
                           progress_color="white",
                           orientation="horizontal",
                           command=update_rows_label)
RowsSlider.place(x=10, y=40)

# Папка сохранения
SaveDirectory = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
SaveDirectory.place(x=25, y=450)

folder_path = StringVar()
SaveDirectoryLabel = CTkLabel(SaveDirectory,
                              text="Папка сохранения:",
                              text_color="white",
                              font=("Arial", 16))
SaveDirectoryLabel.place(x=120, y=5)

# Текстовое поле для отображения пути сохранения
SaveDirectoryPath = CTkEntry(SaveDirectory, height=30, width=250, corner_radius=2, state='readonly')
SaveDirectoryPath.place(x=10, y=35)

def select_save_directory():
    directory = filedialog.askdirectory()
    if directory:
        folder_path.set(directory)
        SaveDirectoryPath.configure(state='normal')
        SaveDirectoryPath.delete(0, 'end')
        SaveDirectoryPath.insert(0, directory)
        SaveDirectoryPath.configure(state='readonly')

SelectDirectoryButton = CTkButton(SaveDirectory,
                                  text="Выбрать папку",
                                  height=30,
                                  width=50,
                                  fg_color="#660066",
                                  command=select_save_directory)
SelectDirectoryButton.place(x=260, y=35)

# Название PDF файла
NameOfFile = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
NameOfFile.place(x=25, y=550)

NameOfPDFFileLabel = CTkLabel(NameOfFile,
                              text="Название файла:",
                              text_color="white",
                              font=("Arial", 16))
NameOfPDFFileLabel.place(x=120, y=5)

# Текстовое поле для названия PDF файла
NameOfPDFFile = CTkEntry(NameOfFile, height=30, width=360, corner_radius=2)
NameOfPDFFile.place(x=10, y=35)

# Кнопка сгенерировать
GenerateFileButton = CTkButton(master=RightFrame,
                               text="Сгенерировать PDF файл",
                               width=250,
                               height=60,
                               text_color="white",
                               font=("Arial", 16),
                               fg_color="#660066",
                               command=generate_qr_codes)  # Исправлено
GenerateFileButton.place(x=80, y=625)

update_column_slider()
QRCodeGenerator.mainloop()
