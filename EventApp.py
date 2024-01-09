import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector

# Function to store event in the MySQL database
def store_event_in_database():
    event_name = event_name_entry.get()
    registration_link = registration_link_entry.get()
    event_image_path = event_image_path_entry.get()

    if not event_name or not registration_link or not event_image_path:
        messagebox.showerror("Error", "Event name, registration link, and event image are required")
        return

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # MySQL username
            password="",  # MySQL password
            database="events"  # Database name
        )

        cursor = connection.cursor()

        insert_query = "INSERT INTO events (event_name, registration_link, event_image_path) VALUES (%s, %s, %s)"
        data = (event_name, registration_link, event_image_path)

        cursor.execute(insert_query, data)
        connection.commit()

        cursor.close()
        connection.close()
        messagebox.showinfo("Success", "Event stored in the database!")

        # Clear the input fields after a successful addition
        event_name_entry.delete(0, tk.END)
        registration_link_entry.delete(0, tk.END)
        event_image_path_entry.delete(0, tk.END)

        # Refresh the event list
        refresh_event_list()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Function to open the registration link
def open_registration_link():
    selected_item = event_listbox.get(event_listbox.curselection())
    if selected_item:
        event = event_details[selected_item]
        registration_link = event['registration_link']
        if registration_link:
            import webbrowser
            webbrowser.open(registration_link)

# Function to delete the selected event
def delete_event():
    selected_item = event_listbox.get(event_listbox.curselection())
    if selected_item:
        event = event_details[selected_item]
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",  # MySQL username
                password="",  # MySQL password
                database="events"  # Database name
            )

            cursor = connection.cursor()

            delete_query = "DELETE FROM events WHERE event_name = %s"
            data = (selected_item,)

            cursor.execute(delete_query, data)
            connection.commit()

            cursor.close()
            connection.close()
            messagebox.showinfo("Success", "Event deleted from the database!")
            
            selected_event_image_label.config(image=None)
            event_listbox.delete(event_listbox.curselection())

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            if connection is not None and connection.is_connected():
                cursor.close()
                connection.close()


# Function to browse for an event image
def browse_event_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
    event_image_path_entry.delete(0, tk.END)
    event_image_path_entry.insert(0, file_path)

# Function to display the selected event's image
def display_selected_event_image(event):
    selected_item = event_listbox.get(event_listbox.curselection())
    if selected_item:
        event = event_details.get(selected_item, {})
        image_path = event.get('event_image_path', None)
        if image_path:
            image = Image.open(image_path)
            image.thumbnail((500, 500))  # Resize the image to fit in the label
            img = ImageTk.PhotoImage(image)
            selected_event_image_label.config(image=img)
            selected_event_image_label.image = img  # Keep a reference to avoid garbage collection
        else:
            # No image path for the selected event, clear the image label
            selected_event_image_label.config(image=None)
    else:
        # No item is selected, so clear the image label
        selected_event_image_label.config(image=None)


# Function to refresh the event list
def refresh_event_list():
    event_listbox.delete(0, tk.END)
    event_details.clear()  # Clear the event details dictionary
    load_events()  # Load events from the database

# Function to load events from the database
def load_events():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # MySQL username
            password="",  # MySQL password
            database="events"  # Database name
        )

        cursor = connection.cursor()

        select_query = "SELECT event_name, registration_link, event_image_path FROM events"
        cursor.execute(select_query)

        for (event_name, registration_link, event_image_path) in cursor:
            event_listbox.insert(tk.END, event_name)
            event_details[event_name] = {'registration_link': registration_link, 'event_image_path': event_image_path}

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Function to restrict permissions for regular users
def restrict_permissions():
    add_event_button.config(state=tk.DISABLED)
    delete_button.config(state=tk.DISABLED)

# Function to handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "Admin@123":
        # Redirect to the admin page
        restrict_permissions()
        show_admin_interface()
        username_entry.config(state=tk.DISABLED)
        password_entry.config(state=tk.DISABLED)
    else:
        # Redirect to the regular user page (view-only)
        show_regular_user_interface()
        username_entry.config(state=tk.DISABLED)
        password_entry.config(state=tk.DISABLED)

def show_admin_interface():
    # Show all the widgets for admin
    add_event_button.config(state=tk.NORMAL)
    delete_button.config(state=tk.NORMAL)
    event_name_entry.config(state=tk.NORMAL)
    registration_link_entry.config(state=tk.NORMAL)
    event_image_path_entry.config(state=tk.NORMAL)
    browse_button.config(state=tk.NORMAL)

def show_regular_user_interface():
    # Show only the widgets for regular users (view-only)
    add_event_button.config(state=tk.DISABLED)
    delete_button.config(state=tk.DISABLED)
    event_name_entry.config(state=tk.DISABLED)
    registration_link_entry.config(state=tk.DISABLED)
    event_image_path_entry.config(state=tk.DISABLED)
    browse_button.config(state=tk.DISABLED)

app = tk.Tk()
app.title("Event Registration")

# Create and configure widgets for login
username_label = tk.Label(app, text="Username:")
username_entry = tk.Entry(app)

password_label = tk.Label(app, text="Password:")
password_entry = tk.Entry(app, show="*")  # Mask the password

login_button = tk.Button(app, text="Login", command=login)

username_label.grid(row=0, column=0)
username_entry.grid(row=0, column=1)

password_label.grid(row=1, column=0)
password_entry.grid(row=1, column=1)

login_button.grid(row=2, columnspan=2)

# Create and configure widgets for adding events
event_name_label = tk.Label(app, text="Event Name:")
event_name_entry = tk.Entry(app, state=tk.DISABLED)  # Disabled by default

registration_link_label = tk.Label(app, text="Registration Link:")
registration_link_entry = tk.Entry(app, state=tk.DISABLED)  # Disabled by default

event_image_label = tk.Label(app, text="Event Image:")
event_image_path_entry = tk.Entry(app, state=tk.DISABLED)  # Disabled by default
browse_button = tk.Button(app, text="Browse", command=browse_event_image, state=tk.DISABLED)  # Disabled by default

add_event_button = tk.Button(app, text="Add Event", command=store_event_in_database, state=tk.DISABLED)  # Disabled by default

event_name_label.grid(row=3, column=0)
event_name_entry.grid(row=3, column=1)

registration_link_label.grid(row=4, column=0)
registration_link_entry.grid(row=4, column=1)

event_image_label.grid(row=5, column=0)
event_image_path_entry.grid(row=5, column=1)
browse_button.grid(row=5, column=2)

add_event_button.grid(row=6, columnspan=3)

# Create and configure widgets for viewing and managing events
event_listbox = tk.Listbox(app, selectmode=tk.SINGLE)
event_listbox.grid(row=7, column=0, columnspan=3)
event_listbox.bind("<<ListboxSelect>>", display_selected_event_image)

view_link_button = tk.Button(app, text="Open Link", command=open_registration_link)
view_link_button.grid(row=8, column=0)

delete_button = tk.Button(app, text="Delete Event", command=delete_event, state=tk.DISABLED)  # Disabled by default
delete_button.grid(row=8, column=1)

event_details = {}  # Dictionary to store event details

# Create a label to display the selected event's image
selected_event_image_label = tk.Label(app)
selected_event_image_label.grid(row=3, column=3, rowspan=6)
refresh_event_list()
app.mainloop()
