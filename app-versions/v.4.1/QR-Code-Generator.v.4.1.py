from tkinter import IntVar, filedialog, messagebox, StringVar
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkCheckBox, CTkOptionMenu
import qrcode
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, red, white
import os

# ==================================================
# =============== Инициализация окна ===============
# ==================================================

QRCodeGenerator = ctk.CTk()
QRCodeGenerator.title("QR Code Generator by: DevSquad")
QRCodeGenerator.geometry("865x800")
QRCodeGenerator.resizable(False, False)
ctk.set_appearance_mode("dark")

# ===================================================
# =============== Дефолтные настройки ===============
# ===================================================

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

# ===================================================
# =============== Переменные и списки ===============
# ===================================================

specific_numbers = []  # Список для хранения конкретных номеров
duplicates_var = ctk.StringVar(QRCodeGenerator, value="1")  # Переменная для хранения количества дубликатов
QRSizeVar = ctk.IntVar(QRCodeGenerator)
SettingsVar = ctk.IntVar(QRCodeGenerator, value=0)  # Установлено значение 0 по умолчанию
specific_numbers_checkbox = ctk.IntVar(QRCodeGenerator)
single_qr_mode = ctk.IntVar(QRCodeGenerator)
folder_path = ctk.StringVar(QRCodeGenerator)
selected_qr_index = -1  # Индекс выбранного QR-кода


# =======================================
# =============== Функции ===============
# =======================================

def validate_entry_input(new_value):
    return new_value.isdigit() and len(new_value) <= 4 or new_value == ""


def add_qr_code():
    """Добавление нового QR-кода в список"""
    qr_number = qr_entry.get().strip()

    # Проверка ввода
    if not qr_number.isdigit() or len(qr_number) != 4:
        messagebox.showerror("Ошибка", "Введите ровно 4 цифры")
        return

    number = int(qr_number)

    # Проверка на дубликаты
    if number in specific_numbers:
        messagebox.showerror("Ошибка", "Такой номер уже есть в списке")
        return

    # Добавляем номер в список
    specific_numbers.append(number)
    update_qr_list()
    qr_entry.delete(0, 'end')  # Очищаем поле ввода


def delete_qr_code():
    """Удаление выбранного QR-кода"""
    global selected_qr_index
    if selected_qr_index == -1:
        messagebox.showerror("Ошибка", "Выберите QR-код для удаления")
        return

    del specific_numbers[selected_qr_index]
    selected_qr_index = -1
    update_qr_list()


def select_qr_code(index):
    """Выбор QR-кода из списка"""
    global selected_qr_index
    selected_qr_index = index
    update_qr_list()


def update_qr_list():
    """Обновление списка QR-кодов в ScrollView"""
    # Очищаем текущий список
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Добавляем элементы из списка
    for i, number in enumerate(specific_numbers):
        qr_frame = ctk.CTkFrame(
            scrollable_frame,
            width=340,
            height=50,
            corner_radius=4,
            fg_color="#555555" if i != selected_qr_index else "#660066"
        )
        qr_frame.pack(pady=5, padx=5, fill='x')

        label = ctk.CTkLabel(
            qr_frame,
            text=f"{number:04d}",
            text_color="white",
            font=("Arial", 14)
        )
        label.place(x=10, y=10)

        # Привязываем клик по фрейму к выбору QR-кода
        qr_frame.bind("<Button-1>", lambda e, idx=i: select_qr_code(idx))
        label.bind("<Button-1>", lambda e, idx=i: select_qr_code(idx))


def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)


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
        COORD_NUM = 1.25 * mm
        FONT_SIZE = 12
        DOP_QR = 0

    update_column_slider()


def update_column_slider():
    ColumnSlider.configure(to=QR_COLUMNS_MAX)
    RowsSlider.configure(to=QR_ROWS_MAX)


def create_qr_pdf(filename, numbers_list):
    temp_folder = os.path.join(os.path.dirname(__file__), 'raw_qr_code')
    os.makedirs(temp_folder, exist_ok=True)

    # Размер страницы с учетом настроек столбцов/строк
    PAGE_WIDTH = (QR_COLUMNS * BACKGROUND_WIDTH + (QR_COLUMNS - 1) * PADDING) + 10 * mm
    PAGE_HEIGHT = (QR_ROWS * BACKGROUND_HEIGHT + (QR_ROWS - 1) * PADDING) + 10 * mm

    c = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # Центрируем QR-коды на странице
    x_start = (PAGE_WIDTH - (QR_COLUMNS * BACKGROUND_WIDTH + (QR_COLUMNS - 1) * PADDING)) / 2
    y_start = (PAGE_HEIGHT - (QR_ROWS * BACKGROUND_HEIGHT + (QR_ROWS - 1) * PADDING)) / 2

    current_number_index = 0
    while current_number_index < len(numbers_list):
        for row in range(QR_ROWS):
            for col in range(QR_COLUMNS):
                if current_number_index >= len(numbers_list):
                    break

                x = x_start + col * (BACKGROUND_WIDTH + PADDING)
                y = y_start + (QR_ROWS - row - 1) * (BACKGROUND_HEIGHT + PADDING)
                number = numbers_list[current_number_index]

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(f"https://app.akku-batt.rent/scooters?number={number:04d}")
                qr.make(fit=True)

                # Рисуем фон
                c.setStrokeColor(red)
                c.setFillColor(white)
                c.roundRect(x, y, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, radius=CORNER_RADIUS, fill=1, stroke=1)

                # Сохраняем и рисуем QR-код
                img = qr.make_image(fill_color="black", back_color="white")
                img_path = os.path.join(temp_folder, f"qr_{number:04d}_{row}_{col}.png")
                img.save(img_path)
                c.drawImage(img_path,
                            x + (BACKGROUND_WIDTH - QR_SIZE) / 2,
                            y + (BACKGROUND_HEIGHT - QR_SIZE + 4.3) / COORD_QR,
                            width=QR_SIZE, height=QR_SIZE)

                # Добавляем текст с номером
                c.setFillColor(TEXT_COLOR)
                c.setFont(FONT_NAME, FONT_SIZE)
                text = f"{number:04d}"
                text_width = c.stringWidth(text, FONT_NAME, FONT_SIZE)
                c.drawString(x + (BACKGROUND_WIDTH - text_width) / 2, y + COORD_NUM, text)

                current_number_index += 1

            if current_number_index >= len(numbers_list):
                break

        if current_number_index < len(numbers_list):
            c.showPage()

    c.save()


def create_single_qr_pdf(filename, number, duplicates):
    temp_folder = os.path.join(os.path.dirname(__file__), 'raw_qr_code')
    os.makedirs(temp_folder, exist_ok=True)

    # Размер страницы для одного QR-кода
    PAGE_WIDTH = BACKGROUND_WIDTH + 10 * mm
    PAGE_HEIGHT = BACKGROUND_HEIGHT + 10 * mm

    c = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for i in range(duplicates):
        # Центрируем QR-код на странице
        x = (PAGE_WIDTH - BACKGROUND_WIDTH) / 2
        y = (PAGE_HEIGHT - BACKGROUND_HEIGHT) / 2

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"https://app.akku-batt.rent/scooters?number={number:04d}")
        qr.make(fit=True)

        # Рисуем рамку
        c.setStrokeColor("#333333")
        c.setFillColor("#333333")
        c.roundRect(x, y, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, radius=CORNER_RADIUS, fill=1, stroke=1)

        # Белый прямоугольник для QR-кода
        inner_padding = 3 * mm
        c.setStrokeColor(white)
        c.setFillColor(white)
        c.roundRect(x + inner_padding, y + inner_padding,
                    BACKGROUND_WIDTH - 2 * inner_padding, BACKGROUND_HEIGHT - 2 * inner_padding,
                    radius=CORNER_RADIUS / 2, fill=1, stroke=1)

        # Сохраняем и рисуем QR-код
        img = qr.make_image(fill_color="black", back_color="white")
        img_path = os.path.join(temp_folder, f"qr_{number:04d}_{i}.png")
        img.save(img_path)
        c.drawImage(img_path,
                    x + (BACKGROUND_WIDTH - QR_SIZE) / 2,
                    y + (BACKGROUND_HEIGHT - QR_SIZE) / 2,
                    width=QR_SIZE, height=QR_SIZE)

        if i < duplicates - 1:  # Не добавляем новую страницу для последнего дубликата
            c.showPage()

    c.save()


def generate_qr_codes():
    try:
        # Проверка выбора размера QR-кода
        if not QRSizeVar.get():
            messagebox.showwarning("Внимание", "Пожалуйста, выберите размер QR-кода.")
            return

        folder = folder_path.get()
        pdf_name = NameOfPDFFile.get()

        if not folder or not pdf_name:
            messagebox.showwarning("Внимание", "Папка и название файла не могут быть пустыми.")
            return

        if single_qr_mode.get():
            # Режим единичного QR-кода
            if not single_qr_number.get():
                messagebox.showwarning("Внимание", "Введите номер для единичного QR-кода.")
                return
            try:
                number = int(single_qr_number.get())
                if len(single_qr_number.get()) != 4:
                    messagebox.showerror("Ошибка", "Номер должен содержать ровно 4 цифры")
                    return

                duplicates = int(duplicates_var.get())
                filename = os.path.join(folder, f"{pdf_name}.pdf")

                if os.path.exists(filename):
                    response = messagebox.askyesno("Файл уже существует",
                                                   f"Файл '{pdf_name}.pdf' уже существует в папке '{folder}'. Хотите перезаписать его?")
                    if not response:
                        return

                create_single_qr_pdf(filename, number, duplicates)
                messagebox.showinfo("Успех",
                                    f"PDF файл '{pdf_name}.pdf' с {duplicates} QR-кодами успешно создан в '{folder}'!")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный номер (целое число).")
        else:
            filename = os.path.join(folder, f"{pdf_name}.pdf")

            if os.path.exists(filename):
                response = messagebox.askyesno("Файл уже существует",
                                               f"Файл '{pdf_name}.pdf' уже существует в папке '{folder}'. Хотите перезаписать его?")
                if not response:
                    return

            if specific_numbers_checkbox.get():  # Используем список из правого фрейма
                if not specific_numbers:
                    messagebox.showwarning("Внимание", "Список конкретных номеров пуст.")
                    return

                # Для поштучных QR-кодов учитываем количество дубликатов
                expanded_list = []
                for number in specific_numbers:
                    expanded_list.extend([number] * int(duplicates_var.get()))

                numbers_list = expanded_list
            else:
                # Для диапазона QR-кодов проверяем ввод
                if not RangeToQRFrom.get() or not RangeOfQRTo.get():
                    messagebox.showerror("Ошибка", "Заполните поля 'От' и 'До'")
                    return

                if len(RangeToQRFrom.get()) != 4 or len(RangeOfQRTo.get()) != 4:
                    messagebox.showerror("Ошибка", "Номера должны содержать ровно 4 цифры")
                    return

                start_num = int(RangeToQRFrom.get())
                end_num = int(RangeOfQRTo.get())

                if start_num > end_num:
                    messagebox.showerror("Ошибка", "Начальный номер не может быть больше конечного.")
                    return

                numbers_list = list(range(start_num, end_num + 1))

            create_qr_pdf(filename, numbers_list)
            messagebox.showinfo("Успех", f"PDF файл '{pdf_name}.pdf' успешно создан в '{folder}'!")

    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числа для диапазона.")


def update_column_label(value):
    global QR_COLUMNS
    SliderColumnValueLabel.configure(text=f"Кол-во столбцов: {int(value)}")
    QR_COLUMNS = int(value)


def update_rows_label(value):
    global QR_ROWS
    SliderRowsValueLabel.configure(text=f"Кол-во строк: {int(value)}")
    QR_ROWS = int(value)


def toggle_qr_entry_state():
    if specific_numbers_checkbox.get():
        qr_entry.configure(state='normal')
        add_button.configure(state='normal')
    else:
        qr_entry.configure(state='disabled')
        add_button.configure(state='disabled')


# ========== ИНТЕРФЕЙС ==========

# Основной фрейм
LeftFrame = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=6,
    fg_color="#333333",
    width=415,
    height=740)
LeftFrame.place(x=7.5, y=30)

# Размер QR кодов
SizeOfQR = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
SizeOfQR.place(x=25, y=50)

SizeOfQrLabel = CTkLabel(master=SizeOfQR,
                         text_color="white",
                         font=("Arial", 18),
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
    height=120)
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

validate_cmd = QRCodeGenerator.register(validate_entry_input)

RangeToQRFrom = CTkEntry(
    RangeOfQR,
    height=30,
    width=70,
    corner_radius=2,
    validate='key',
    validatecommand=(validate_cmd, '%P')
)
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
    corner_radius=2,
    validate='key',
    validatecommand=(validate_cmd, '%P')
)
RangeOfQRTo.place(x=270, y=37)

specific_numbers_checkbox = ctk.CTkCheckBox(
    RangeOfQR,
    text="Использовать список номеров (справа)",
    variable=specific_numbers_checkbox,
    fg_color="#660066",
    text_color="white",
    font=("Arial", 12),
    command=toggle_qr_entry_state  # Используем command для привязки функции
)
specific_numbers_checkbox.place(x=60, y=80)

# Фрейм для единичного QR-кода
single_qr_frame = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=120)
single_qr_frame.place_forget()

single_qr_label = CTkLabel(single_qr_frame,
                           text="Единичный QR-код",
                           text_color="white",
                           font=("Arial", 16))
single_qr_label.place(x=120, y=5)

single_qr_number_label = CTkLabel(single_qr_frame,
                                  text="Номер:",
                                  text_color="white",
                                  font=("Arial", 14))
single_qr_number_label.place(x=37, y=36)

single_qr_number = CTkEntry(
    single_qr_frame,
    height=30,
    width=70,
    corner_radius=2)
single_qr_number.place(x=87, y=37)

# Кол-во в столбец
ColumnQrOnList = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
ColumnQrOnList.place(x=25, y=280)

SliderColumnValueLabel = ctk.CTkLabel(ColumnQrOnList,
                                      text="Кол-во столбцов: 1",
                                      fg_color="#444343",
                                      text_color="white",
                                      font=("Arial", 16))
SliderColumnValueLabel.place(x=120, y=5)

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
RowsQrOnList.place(x=25, y=380)

SliderRowsValueLabel = ctk.CTkLabel(RowsQrOnList,
                                    text="Кол-во строк: 1",
                                    fg_color="#444343",
                                    text_color="white",
                                    font=("Arial", 16))
SliderRowsValueLabel.place(x=130, y=5)

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
SaveDirectory.place(x=25, y=480)

SaveDirectoryLabel = CTkLabel(SaveDirectory,
                              text="Папка сохранения:",
                              text_color="white",
                              font=("Arial", 16))
SaveDirectoryLabel.place(x=120, y=5)

SaveDirectoryPath = CTkEntry(SaveDirectory,
                             height=30,
                             width=250,
                             corner_radius=2,
                             state='readonly',
                             textvariable=folder_path)
SaveDirectoryPath.place(x=10, y=35)

SelectDirectoryButton = CTkButton(SaveDirectory,
                                  text="Выбрать папку",
                                  height=30,
                                  width=50,
                                  fg_color="#660066",
                                  command=select_folder)
SelectDirectoryButton.place(x=260, y=35)

# Название PDF файла
NameOfFile = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=4,
    fg_color="#444343",
    width=380,
    height=80)
NameOfFile.place(x=25, y=580)

NameOfPDFFileLabel = CTkLabel(NameOfFile,
                              text="Название файла:",
                              text_color="white",
                              font=("Arial", 16))
NameOfPDFFileLabel.place(x=120, y=5)

NameOfPDFFile = CTkEntry(NameOfFile, height=30, width=360, corner_radius=2)
NameOfPDFFile.place(x=10, y=35)

# Кнопка сгенерировать
GenerateFileButton = CTkButton(master=LeftFrame,
                               text="Сгенерировать PDF файл",
                               width=250,
                               height=60,
                               text_color="white",
                               font=("Arial", 16),
                               fg_color="#660066",
                               command=generate_qr_codes)
GenerateFileButton.place(x=80, y=655)

# Правый фрейм
RightFrame = ctk.CTkFrame(
    QRCodeGenerator,
    corner_radius=6,
    fg_color="#333333",
    width=415,
    height=740)
RightFrame.place(x=442, y=30)

# Фрейм для одиночных QR-кодов
SingleQRFrame = ctk.CTkFrame(
    RightFrame,
    corner_radius=4,
    fg_color="#444343",
    width=385,
    height=130)
SingleQRFrame.place(x=15, y=20)

# Заголовок
SingleQRLabel = ctk.CTkLabel(
    master=SingleQRFrame,
    text_color="white",
    font=("Arial", 18),
    text='Поштучные QR коды')
SingleQRLabel.place(x=105, y=5)

# Поле ввода и кнопка добавления
qr_entry = ctk.CTkEntry(
    SingleQRFrame,
    width=150,
    height=30,
    placeholder_text="Введите 4 цифры",
    justify='center',
    state='disabled'
)
qr_entry.place(x=20, y=50)

add_button = ctk.CTkButton(
    SingleQRFrame,
    text="+",
    width=30,
    height=30,
    fg_color="#660066",
    command=add_qr_code,
    state='disabled'
)
add_button.place(x=180, y=50)

delete_button = ctk.CTkButton(
    SingleQRFrame,
    text="Удалить",
    width=80,
    height=30,
    fg_color="#990000",
    command=delete_qr_code
)
delete_button.place(x=280, y=50)

# Выбор количества повторений
duplicates_label = ctk.CTkLabel(
    SingleQRFrame,
    text="Повторов:",
    text_color="white",
    font=("Arial", 12)
)
duplicates_label.place(x=20, y=90)

duplicates_menu = ctk.CTkOptionMenu(
    SingleQRFrame,
    values=[str(i) for i in range(1, 11)],
    variable=duplicates_var,
    width=60,
    height=30,
    fg_color="#660066"
)
duplicates_menu.place(x=90, y=90)

# Фрейм для отображения QR кодов (одиночек)
SingleQRScroll = ctk.CTkFrame(
    RightFrame,
    corner_radius=4,
    fg_color="#444343",
    width=385,
    height=555)
SingleQRScroll.place(x=15, y=160)

scrollable_frame = ctk.CTkScrollableFrame(
    SingleQRScroll,
    width=355,
    height=530,
    fg_color="#444343"
)
scrollable_frame.place(x=5, y=5)

QRCodeGenerator.mainloop()
