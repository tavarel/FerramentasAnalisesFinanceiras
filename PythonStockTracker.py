#stock tracker app using python, Yfinance api and tkinter

import yfinance as yf
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import *
from tkinter import font
from tkcalendar import Calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import math 
from pandas_datareader import data as wb
from datetime import datetime
import os
from datetime import timedelta
from datetime import time


#creating the main window
window = tk.Tk()
window.title("Stock Tracker")
window.geometry("1300x900")
window.resizable(False, False)
window.configure(bg="#1a1a1a")

# Database setup
DB_FILE = 'stocks.db'
def init_db():
    if not os.path.isfile(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE stocks (
                id INTEGER PRIMARY KEY,
                ticker TEXT,
                purchase_date TEXT,
                purchase_price REAL
            )
        ''')
        conn.commit()
        conn.close()

init_db()


# Modifique a função save_current_stocks para deletar apenas se houver itens
def save_current_stocks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    children = my_tree.get_children()
    if children:
        c.execute('DELETE FROM stocks')  # Remove os registros antigos apenas se houver itens novos
        for child in children:
            stock_id, ticker, purchase_price, _, _, purchase_date = my_tree.item(child)["values"]
            purchase_price = float(purchase_price)
            c.execute('INSERT INTO stocks (id, ticker, purchase_date, purchase_price) VALUES (?, ?, ?, ?)',
                      (stock_id, ticker, purchase_date, purchase_price))
        conn.commit()
    conn.close()

# Certifique-se de chamar save_current_stocks quando a janela é fechada com o botão (X)
window.protocol("WM_DELETE_WINDOW", exit)


# Modifique a função exit para salvar as ações antes de fechar
def exit():
    save_current_stocks()
    window.destroy()
    
    
def remove_stock_from_db(stock_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM stocks WHERE id = ?', (stock_id,))
    conn.commit()
    conn.close()
    

# Function to get all stocks from the database
def get_all_stocks_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, ticker, purchase_date, purchase_price FROM stocks')
    stocks = c.fetchall()
    conn.close()
    print("Carregado do DB:", stocks)  # Print para depuração
    return stocks


# Function to find the last weekday
def get_last_weekday(date):
    date = datetime.strptime(date, '%Y-%m-%d')
    offset = max(1, (date.weekday() + 6) % 7 - 3)
    timedelta(days=offset)
    return (date - timedelta(days=offset)).strftime('%Y-%m-%d')

#creating the title label
title_label = tk.Label(window, text="Stock Tracker", font=("Arial", 30), bg="#1a1a1a", fg="white")
title_label.pack(pady=10)

#creating the frame for the entry box
entry_frame = tk.Frame(window, bg="#1a1a1a")
entry_frame.pack(pady=10)

#creating the entry box
entry_box = tk.Entry(entry_frame, font=("Arial", 15), width=15)
entry_box.grid(row=0, column=0, padx=10, pady=10)

#creating the search button
search_button = tk.Button(entry_frame, text="Search", font=("Arial", 15), bg="#1a1a1a", fg="white", command=lambda: search(entry_box.get()))
search_button.grid(row=0, column=1, padx=10, pady=10)

# Add a button to open the calendar
cal_button = tk.Button(entry_frame, text="Select Purchase Date", font=("Arial", 15), bg="#1a1a1a", fg="white")
cal_button.grid(row=0, column=2, padx=10)

purchase_date = datetime.now().strftime('%Y-%m-%d')  # Default to today

save_button = tk.Button(entry_frame, text="Save to DB", font=("Arial", 15), bg="#1a1a1a", fg="white", command=lambda: save_and_show_db())
save_button.grid(row=0, column=3, padx=10, pady=10)



def open_calendar():
    top = tk.Toplevel(window)
    cal = Calendar(top, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
    cal.pack(pady=10, padx=10)

    def grab_date():
        global purchase_date
        purchase_date = datetime.strptime(cal.get_date(), '%m/%d/%y').strftime('%Y-%m-%d')
        top.destroy()

    select_button = tk.Button(top, text="Select", command=grab_date)
    select_button.pack(pady=10)

cal_button.config(command=open_calendar)

#creating the frame for the labels
label_frame = tk.Frame(window, bg="#1a1a1a")
label_frame.pack(pady=10)

#creating the labels
name_label = tk.Label(label_frame, text="Name", font=("Arial", 15), bg="#1a1a1a", fg="white")
name_label.grid(row=0, column=0, padx=10, pady=10)

price_label = tk.Label(label_frame, text="Price", font=("Arial", 15), bg="#1a1a1a", fg="white")
price_label.grid(row=0, column=1, padx=10, pady=10)

change_label = tk.Label(label_frame, text="Change", font=("Arial", 15), bg="#1a1a1a", fg="white")
change_label.grid(row=0, column=2, padx=10, pady=10)

percent_change_label = tk.Label(label_frame, text="% Change", font=("Arial", 15), bg="#1a1a1a", fg="white")
percent_change_label.grid(row=0, column=3, padx=10, pady=10)

purchase_date_label = tk.Label(label_frame, text="Purchase Date (YYYY-MM-DD)", font=("Arial", 15), bg="#1a1a1a", fg="white")

#creating the frame for the treeview
tree_frame = tk.Frame(window)
tree_frame.pack(pady=10)

#creating the treeview
tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
my_tree.pack()

tree_scroll.config(command=my_tree.yview)

my_tree['columns'] = ("ID", "Name", "Price", "Change", "% Change", "Purchase Date")


my_tree.column("#0", width=0, stretch=tk.NO)
my_tree.column("Name", anchor=tk.W, width=120)
my_tree.column("Price", anchor=tk.CENTER, width=100)
my_tree.column("Change", anchor=tk.CENTER, width=100)
my_tree.column("% Change", anchor=tk.CENTER, width=100)
my_tree.column("ID", anchor=tk.CENTER, width=120)  # Nova coluna para ID


my_tree.heading("#0", text="", anchor=tk.W)
my_tree.heading("Name", text="Name", anchor=tk.W)
my_tree.heading("Price", text="Price", anchor=tk.CENTER)
my_tree.heading("Change", text="Change", anchor=tk.CENTER)
my_tree.heading("% Change", text="% Change", anchor=tk.CENTER)
my_tree.heading("ID", text="ID", anchor=tk.CENTER)  # Nova coluna para ID
my_tree.heading("Purchase Date", text="Purchase Date (YYYY-MM-DD)", anchor=tk.CENTER)

#creating the frame for the bottom buttons
bottom_frame = tk.Frame(window, bg="#1a1a1a")
bottom_frame.pack(pady=10)

#creating the bottom buttons
graph_button = tk.Button(bottom_frame, text="Graph", font=("Arial", 15), bg="#1a1a1a", fg="white", command=lambda: graph())
graph_button.grid(row=0, column=0, padx=10, pady=10)

clear_button = tk.Button(bottom_frame, text="Clear", font=("Arial", 15), bg="#1a1a1a", fg="white", command=lambda: clear())
clear_button.grid(row=0, column=1, padx=10, pady=10)

update_db_button = tk.Button(bottom_frame, text="Update DB", font=("Arial", 15), bg="#1a1a1a", fg="white", command=lambda: update_db())
update_db_button.grid(row=0, column=2, padx=10, pady=10)

# Initialize this frame for the 'Open Interactive Window' button and place it at the top
top_frame = tk.Frame(window, bg="#1a1a1a")
top_frame.pack(side='top', fill='x', pady=10)

NUMBER_OF_BOXES_PER_ROW = 3

def open_interactive_window():
    # Create a new window
    interactive_window = tk.Toplevel(window)
    interactive_window.title("Interactive Stock Tracker")
    interactive_window.geometry("800x600")
    interactive_window.configure(bg="#1a1a1a")

    # Timer label
    timer_label = tk.Label(interactive_window, text="Time until reload: 15 seconds", bg="#1a1a1a", fg="white")
    timer_label.pack(pady=10)

    # Stocks frame
    stocks_frame = tk.Frame(interactive_window, bg="#1a1a1a")
    stocks_frame.pack(fill='both', expand=True)

    # Function to create a stock display box
    def create_stock_box(row_frame, column, ticker, company_name, current_price, percent_change, purchase_date, last_price=None):
        box_frame = tk.Frame(row_frame, bg="#333333", relief="groove", bd=2)
        box_frame.grid(row=0, column=column, pady=15, padx=15, sticky="nsew")
        box_frame.grid_columnconfigure(0, weight=1)

        tk.Label(box_frame, text=f"Ticker: {ticker}", bg="#333333", fg="white").pack(fill='x')
        tk.Label(box_frame, text=f"Company: {company_name}", bg="#333333", fg="white").pack(fill='x')
        price_label = tk.Label(box_frame, text=f"Current Price: {current_price:.2f}", bg="#333333", fg="white")
        price_label.pack(fill='x')
        
        # Change the color of the percentage based on its value
        percent_color = "green" if percent_change >= 0 else "red"
        percent_label = tk.Label(box_frame, text=f"Percentage Change: {percent_change:.2f}%", bg="#333333", fg=percent_color)
        percent_label.pack(fill='x')
        tk.Label(box_frame, text=f"Purchase Date: {purchase_date}", bg="#333333", fg="white").pack(fill='x')

        # Flash animation if the price has changed
        if last_price is not None and current_price != last_price:
            box_frame.configure(bg="white")
            interactive_window.after(100, lambda: box_frame.configure(bg="#333333"))

        return box_frame
    
    def update_stock_values(last_prices=None):
        last_prices = last_prices or {}
        for widget in stocks_frame.winfo_children():
            widget.destroy()

        row_frames = []
        stocks = get_all_stocks_from_db()
        for index, stock in enumerate(stocks):
            row = index // NUMBER_OF_BOXES_PER_ROW
            column = index % NUMBER_OF_BOXES_PER_ROW

            # Create a new row if needed
            if len(row_frames) <= row:
                row_frame = tk.Frame(stocks_frame, bg="#1a1a1a")
                row_frame.pack(fill='x', expand=True)
                row_frames.append(row_frame)

            ticker, purchase_date = stock[1], stock[2]
            stock_obj = yf.Ticker(ticker)
            hist = stock_obj.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                percent_change = (current_price - hist['Open'].iloc[0]) / hist['Open'].iloc[0] * 100
                last_price = last_prices.get(ticker)

                # Create the stock box
                box_frame = create_stock_box(row_frames[row], column, ticker, stock_obj.info['shortName'], current_price, percent_change, purchase_date, last_price)

                # Update the last known price
                last_prices[ticker] = current_price

        # Schedule the next update
        interactive_window.after(15000, lambda: update_stock_values(last_prices))

    # Start the update process
    update_stock_values()

    def update_timer(seconds):
        if seconds > 0:
            timer_label.config(text=f"Time until reload: {seconds} seconds")
            interactive_window.after(1000, lambda: update_timer(seconds-1))
        else:
            update_stock_values()  # Call your update function
            timer_label.config(text="Time until reload: 15 seconds")
            interactive_window.after(1000, lambda: update_timer(14))

    update_timer(15)  # Start the countdown

# Outside of your function, make sure to bind the button to the function
open_window_button = tk.Button(window, text="Open Interactive Window", font=("Arial", 15), bg="#1a1a1a", fg="white", command=open_interactive_window)
open_window_button.pack(fill='x')


def update_db():
    try:
        update_stock_prices()  # Atualiza os preços no banco de dados e na TreeView
        print_db_contents()    # Imprime os dados do banco de dados atualizados
        messagebox.showinfo("Success", "Database and display updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        
        
#creating the frame for the graph
graph_frame = tk.Frame(window)
graph_frame.pack(pady=10, expand=True, fill='both')

#creating the graph
fig = plt.figure(figsize=(5, 4), dpi=100)
plt.style.use("dark_background")
plt.tight_layout()
plt.grid()
plt.xlabel("Date")
plt.ylabel("Price")
plt.title("Stock Graph")

canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack()

#creating the frame for the bottom buttons
bottom_frame = tk.Frame(window, bg="#1a1a1a")
bottom_frame.pack(pady=10)

#creating the bottom buttons
exit_button = tk.Button(bottom_frame, text="Exit", font=("Arial", 15), bg="#1a1a1a", fg="white", command=lambda: exit())
exit_button.grid(row=0, column=0, padx=10, pady=10)

#function to search for a stock

LAST_IID_FILE = 'last_iid.txt'

def get_last_iid():
    try:
        with open(LAST_IID_FILE, 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

def save_last_iid(iid):
    with open(LAST_IID_FILE, 'w') as f:
        f.write(str(iid))
        
last_iid = get_last_iid()

def search(stock):
    try:
        stock_obj = yf.Ticker(stock)
        today = datetime.now().strftime('%Y-%m-%d')

        global last_iid, purchase_date  # Adicione purchase_date ao escopo global
        last_iid += 1  # Incrementa o iid para garantir que é único
        save_last_iid(last_iid)
        
        # Use the global purchase_date set by the calendar
        purchase_date_adjusted = get_last_weekday(purchase_date)
        hist = stock_obj.history(start=purchase_date_adjusted, end=today)
        
        if hist.empty:
            messagebox.showerror("Error", "Stock information is not available")
            return

        price_on_purchase_date = hist['Close'].iloc[0]
        current_price = hist['Close'].iloc[-1]
        change = current_price - price_on_purchase_date
        percent_change = (change / price_on_purchase_date) * 100

        my_tree.insert(parent='', index='end', iid=last_iid, text="", 
                   values=(last_iid, stock, f"{current_price:.2f}", f"{change:.2f}", f"{percent_change:.2f}", purchase_date))
        
        entry_box.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        
        
# Modifique a função update_stock_prices para que ela não se auto-agende
def update_stock_prices():
    for child in my_tree.get_children():
        stock_id, ticker, purchase_price, _, _, purchase_date = my_tree.item(child)["values"]
        purchase_price = float(purchase_price)
        stock_obj = yf.Ticker(ticker)
        today = datetime.now().strftime('%Y-%m-%d')
        hist = stock_obj.history(start=get_last_weekday(purchase_date), end=today)
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            change = current_price - purchase_price
            percent_change = (change / purchase_price) * 100
            my_tree.item(child, values=(stock_id, ticker, f"{current_price:.2f}", f"{change:.2f}", f"{percent_change:.2f}", purchase_date))
        else:
            messagebox.showinfo("Info", f"No new data for {ticker}.")
    save_current_stocks()  # Salva as mudanças no banco de dados após a atualização


# Function to initialize stock prices and update every 15 seconds
def initialize_and_update_prices():
    stocks = get_all_stocks_from_db()
    my_tree.delete(*my_tree.get_children())
    for stock_id, ticker, purchase_date, purchase_price in stocks:
        print(f"Inicializando {ticker} com preço de compra {purchase_price}")
        purchase_price = float(purchase_price) if purchase_price else 0.0
        my_tree.insert(parent='', index='end', iid=stock_id, text="",
                       values=(stock_id, ticker, f"{purchase_price:.2f}", 0, 0, purchase_date))
    # window.after(15000, update_stock_prices)  


                
# Função para limpar uma ação selecionada ou todas as ações se nenhuma estiver selecionada
def clear():
    selected_items = my_tree.selection()
    if selected_items:  # Se há itens selecionados
        for selected_item in selected_items:
            stock_id = my_tree.item(selected_item)["values"][0]
            remove_stock_from_db(stock_id)  # Remove do banco de dados
            my_tree.delete(selected_item)  # Remove da TreeView
    else:
        for child in my_tree.get_children():
            stock_id = my_tree.item(child)["values"][0]
            remove_stock_from_db(stock_id)  # Remove do banco de dados
            my_tree.delete(child)  # Remove da TreeView
    
# Função para gerar o gráfico da ação selecionada
def graph():
    selected = my_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a stock")
        return

    stock_id = selected[0]  # 'selected' é uma lista de IDs selecionados; pegue o primeiro
    ticker = my_tree.item(stock_id)['values'][1]

    try:
        stock_obj = yf.Ticker(ticker)
        df = stock_obj.history(period="180d") # Alterar período para quanto tempo achar necessário

        # Se já existir um gráfico, remova-o antes de criar um novo
        for widget in graph_frame.winfo_children():
            widget.destroy()

        # Criando um novo gráfico
        fig, ax = plt.subplots(figsize=(10, 4))
        df['Close'].plot(ax=ax)

        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.set_title(f"Stock Price of {ticker}")
        

        # Adicionando anotações para a data de início e o preço
        start_date = df.index[0]
        start_price = df['Close'][0]
        ax.annotate(f'Start: {start_date.strftime("%Y-%m-%d")}\nPrice: ${start_price:.2f}',
                    xy=(start_date, start_price), xycoords='data',
                    xytext=(10, -30), textcoords='offset points',
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))

        # Mostrando o gráfico no Tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)  # Use o mesmo nome 'canvas' como no código original
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        canvas.draw()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        
       
       
def save_and_show_db():
    try:
        save_current_stocks()  # Chama a função que salva os dados no banco de dados
        print_db_contents()    # Função auxiliar para imprimir os dados do banco de dados (para depuração)
        messagebox.showinfo("Success", "Data saved to database successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        
def print_db_contents():
    # Função auxiliar para imprimir o conteúdo do banco de dados (para depuração)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM stocks')
    stocks = c.fetchall()
    conn.close()
    print("Current DB contents:", stocks)
    
    


         
#function to exit the program
def exit():
    window.destroy()
    
    
initialize_and_update_prices()
window.mainloop()



        