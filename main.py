import tkinter as tk
from datetime import datetime as dt
from tkinter import *
from tkinter import messagebox, ttk, simpledialog, filedialog

import pandas as pd
import plotly.graph_objs as go
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
from tkinterdnd2 import DND_FILES, TkinterDnD

# CONSTANTS ------------------------------------------------

LIST_OF_FILES = []
LIST_OF_DATA_FRAME = []


# Functions ------------------------------------------------

# --------------------------------------------------------------------------------
# Message ------------------------------------------------------------------------
# --------------------------------------------------------------------------------
def custom_entry_dialog(title, message, callback):
    dialog = tk.Toplevel(root)
    dialog.title(title)
    # Label pour le message
    new_label = tk.Label(dialog, text=message)
    new_label.pack(pady=10)
    # Champ d'entrée pour le délimiteur
    entry_var = tk.StringVar()
    entry = ttk.Entry(dialog, textvariable=entry_var, width=30)
    entry.pack(pady=5)

    # Fonction pour sauvegarder le délimiteur et fermer la boîte de dialogue
    def save_and_close():
        value = entry_var.get()
        if value != "":
            callback(value)
            dialog.destroy()

    # Bouton "OK"
    ok_button = ttk.Button(dialog, text="OK", command=save_and_close)
    ok_button.pack(side="left", padx=5)

    # Fonction pour fermer la boîte de dialogue sans sauvegarder
    def close_dialog():
        dialog.destroy()

    # Bouton "Annuler"
    cancel_button = ttk.Button(dialog, text="Annuler", command=close_dialog)
    cancel_button.pack(side="right", padx=5)
    dialog.transient(root)  # Définit la fenêtre comme dépendante de la fenêtre principale
    dialog.grab_set()  # Empêche l'interaction avec d'autres fenêtres
    root.wait_window(dialog)  # Attend que la boîte de dialogue se ferme


def column_choice_dialog(df, choice):
    texte = ""
    fonction = None
    if choice == "describe":
        texte = "Choisissez une colonne à décrire :"
        fonction = (lambda: describe_selected_column(df, column_var))
    elif choice == "rename":
        texte = "Choisissez une colonne à renommer :"
        fonction = (lambda: rename_column_dialog(df, column_var))

    # Créer une liste des colonnes disponibles dans le DataFrame
    columns = df.columns.tolist()
    # Créer une nouvelle fenêtre pour la boîte de dialogue
    column_dialog = tk.Toplevel(root)
    column_dialog.title("Choix de la colonne")
    # Label pour le message
    new_label = tk.Label(column_dialog, text=texte)
    new_label.pack(pady=10)
    # Créer une Combobox pour afficher les colonnes disponibles
    column_var = tk.StringVar()
    column_combobox = ttk.Combobox(column_dialog, textvariable=column_var, values=columns,
                                   width=max(len(col) for col in columns) + 2)
    column_combobox.pack(pady=(0, 5), padx=10)  # Ajout du padding uniquement en bas
    # Bouton OK
    ok_button = ttk.Button(column_dialog, text="OK", command=fonction)  # Appel de la fonction ici
    ok_button.pack(pady=5)


def handle_contamination_callback(value, df, index):
    try:
        contamination_value = float(value)
        if 0 <= contamination_value <= 1:
            selected_df_name = lb.get(index)  # Récupérer le nom du DataFrame sélectionné
            clean_dataframe(df, selected_df_name,
                            contamination_value)  # Passer le DataFrame, son nom et la valeur de contamination à la fonction clean_dataframe
        else:
            messagebox.showerror("Erreur", "La valeur de contamination doit être comprise entre 0 et 1.")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique pour la contamination.")


def show_entry_dialog(callback):
    custom_entry_dialog("Choix du délimiteur", "Entrez le délimiteur utilisé dans le fichier :", callback)


def contamination_choice(callback):
    custom_entry_dialog("Choix de la contamination",
                        "Entrez une valeur de contamination pour le traitement de vos données (entre 0 et 1)\n\nCette valeur corresponds au pourcentage de données considérées comme des anomalies\nLa contamination contrôle la sensibilité de l'algorithme aux détection d'anomalies.",
                        callback)


def show_attention_message_box():
    messagebox.showerror("Attention", "Le fichier doit être un fichier .csv")


def show_selection_error():
    messagebox.showerror("Attention", "Erreurs lors de l'encodage.")


def show_file_registered():
    messagebox.showinfo("Information", "Le fichier à bien été enregistrer")
    print(LIST_OF_DATA_FRAME)


# --------------------------------------------------------------------------------
# Gestion des boutons ------------------------------------------------------------
# --------------------------------------------------------------------------------
def delete_selected_dataframe():
    try:
        index = lb.curselection()[0]
        del LIST_OF_DATA_FRAME[index]
        lb.delete(index)
    except IndexError:
        pass


def describe_selected_dataframe():
    try:
        index = lb.curselection()[0]
        selected_df = LIST_OF_DATA_FRAME[index]
        column_choice_dialog(selected_df, choice="describe")
    except IndexError:
        pass


def show_columns():
    try:
        index = lb.curselection()[0]
        selected_df = LIST_OF_DATA_FRAME[index]
        columns = [f"{item}\n" for item in selected_df.columns]
        # Création d'une nouvelle fenêtre pour afficher les colonnes
        columns_window = tk.Toplevel(root)
        columns_window.title("Colonnes")
        # Création d'un widget Text pour afficher les colonnes
        text_widget = tk.Text(columns_window, wrap="none", height=10, width=50, selectbackground="blue")
        text_widget.insert("end", "".join(columns))
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        # Ajout d'une barre de défilement pour le texte
        scroll_y = tk.Scrollbar(columns_window, orient="vertical", command=text_widget.yview)
        scroll_y.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scroll_y.set)
    except IndexError:
        pass


def rename_columns():
    try:
        index = lb.curselection()[0]
        selected_df = LIST_OF_DATA_FRAME[index]
        column_choice_dialog(selected_df, choice="rename")
    except IndexError:
        pass


def clean_df():
    try:
        index = lb.curselection()[0]
        selected_df = LIST_OF_DATA_FRAME[index]
        contamination_choice(lambda value: handle_contamination_callback(value, selected_df,
                                                                         index))  # Passer l'index à la fonction de rappel
    except IndexError:
        pass


def register_df():
    try:
        index = lb.curselection()[0]
        selected_df = LIST_OF_DATA_FRAME[index]
        selected_df_name = lb.get(index)  # Récupérer le nom du DataFrame sélectionné
        save_file(selected_df=selected_df, file_name=selected_df_name)
    except IndexError:
        pass


def plot_graph():
    try:
        index = lb.curselection()[0]
        selected_df = LIST_OF_DATA_FRAME[index]
        graphic_column_selection(selected_df)
    except IndexError:
        pass


# --------------------------------------------------------------------------------
# Affichage Graphique ------------------------------------------------------------
# --------------------------------------------------------------------------------
def graphic_column_selection(df):
    # Créer une liste des colonnes disponibles dans le DataFrame
    columns = df.columns.tolist()

    # Créer une nouvelle fenêtre pour la boîte de dialogue
    column_dialog = tk.Toplevel(root)
    column_dialog.title("Choix des colonnes")

    # Label pour le message
    new_label = tk.Label(column_dialog, text="Choisissez les colonnes pour tracer un graphique :")
    new_label.pack(pady=10)

    # Créer une Combobox pour afficher les colonnes disponibles
    label_abscisse = tk.Label(column_dialog, text="Abscisse :")
    label_abscisse.pack(pady=10, padx=10, anchor="w")
    abscisse = tk.StringVar()
    column_combobox = ttk.Combobox(column_dialog,
                                   textvariable=abscisse,
                                   values=columns,
                                   width=max(len(col) for col in columns) + 2)
    column_combobox.pack(pady=(0, 5), padx=10)  # Ajout du padding uniquement en bas

    # Créer une Combobox pour afficher les colonnes disponibles
    label_ordonnee = tk.Label(column_dialog, text="Ordonnée :")
    label_ordonnee.pack(pady=10, padx=10, anchor="w")
    ordonnee = tk.StringVar()
    column_combobox2 = ttk.Combobox(column_dialog,
                                    textvariable=ordonnee,
                                    values=columns,
                                    width=max(len(col) for col in columns) + 2)
    column_combobox2.pack(pady=(0, 5), padx=10)  # Ajout du padding uniquement en bas

    # Fonction pour décrire la colonne sélectionnée
    def graphics_column(selected_df):
        abscisse_column = abscisse.get()
        ordonnee_column = ordonnee.get()
        if abscisse_column and ordonnee_column:
            # Créer un graphique Plotly interactif
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=selected_df[abscisse_column], y=selected_df[ordonnee_column], mode='lines+markers',
                           name='Sales'))
            # Mise à jour des paramètres esthétiques
            fig.update_traces(marker=dict(size=6, color='navy'), line=dict(width=2, color='darkcyan'))
            fig.update_layout(title=f"Graphique de {ordonnee_column} en fonction de {abscisse_column}",
                              xaxis_title=abscisse_column,
                              yaxis_title=ordonnee_column,
                              font=dict(size=12),
                              plot_bgcolor='white',  # Couleur de fond du graphique
                              paper_bgcolor='rgba(0,0,0,0)',  # Couleur de fond du papier
                              hovermode='x',  # Mode de survol
                              margin=dict(l=50, r=50, t=50, b=50),  # Marges
                              xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                              # Afficher la grille de l'axe x avec une couleur plus claire
                              yaxis=dict(showgrid=True, gridcolor='lightgrey'),
                              # Afficher la grille de l'axe y avec une couleur plus claire
                              )
            fig.update_xaxes(rangeslider_visible=True)
            # Afficher le graphique interactif
            fig.show()

    # Bouton OK
    ok_button = ttk.Button(column_dialog, text="OK", command=lambda: graphics_column(selected_df=df))
    ok_button.pack(pady=5)


# --------------------------------------------------------------------------------
# Combinaison de 2 DataFrame ------------------------------------------------------------
# --------------------------------------------------------------------------------
def combination_selection():
    list_of_df = [lb.get(i) for i in range(lb.size())]
    if lb.size() == 0:
        return
    else:
        # Créer une nouvelle fenêtre pour la boîte de dialogue
        df_dialogue = tk.Toplevel(root)
        df_dialogue.title("Choix des DataFrames")

        # Centrer la fenêtre
        window_width = 500
        window_height = 350
        screen_width = df_dialogue.winfo_screenwidth()
        screen_height = df_dialogue.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        df_dialogue.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")

        # Label pour le message
        new_label = tk.Label(df_dialogue,
                             text="Choisissez les DataFrames à combiner ainsi que la colonne sur laquelle les combiner :")
        new_label.pack(pady=10)

        # Créer une Combobox pour afficher les df disponibles
        label_df_1 = tk.Label(df_dialogue, text="DataFrame 1 :")
        label_df_1.pack(pady=10, padx=10, anchor="w")
        df_1 = tk.StringVar()
        df_combobox1 = ttk.Combobox(df_dialogue,
                                    textvariable=df_1,
                                    values=list_of_df,
                                    width=30)  # Ajuster la largeur selon le contenu
        df_combobox1.pack(pady=(0, 5), padx=10)  # Ajout du padding uniquement en bas

        # Créer une Combobox pour afficher les df disponibles
        label_df_2 = tk.Label(df_dialogue, text="DataFrame 2 :")
        label_df_2.pack(pady=10, padx=10, anchor="w")
        df_2 = tk.StringVar()
        df_combobox2 = ttk.Combobox(df_dialogue,
                                    textvariable=df_2,
                                    values=[],  # Les valeurs seront mises à jour dynamiquement
                                    width=30)  # Ajuster la largeur selon le contenu
        df_combobox2.pack(pady=(0, 5), padx=10)  # Ajout du padding uniquement en bas

        def update_df2_values():
            df_combobox2.set('')
            # Mettre à jour les valeurs de la deuxième Combobox
            selected_df1 = df_1.get()
            if selected_df1:
                # Filtrer les DataFrames différents de celui choisi dans la première Combobox
                remaining_dfs = [df for df in list_of_df if df != selected_df1]
                df_combobox2['values'] = remaining_dfs

        # Mettre à jour les valeurs de la deuxième Combobox lorsque la première Combobox est modifiée
        df_1.trace_add('write', lambda *args: update_df2_values())

        def choose_common_column():
            # Désactiver les Combobox df_1 et df_2
            df_combobox1.configure(state="disabled")
            df_combobox2.configure(state="disabled")
            ok_button.configure(state="disabled")
            dataframe_1 = df_1.get()
            dataframe_2 = df_2.get()
            index_1 = lb.get(0, "end").index(dataframe_1)
            index_2 = lb.get(0, "end").index(dataframe_2)
            # Récupérer les DataFrames sélectionnés
            selected_df1 = LIST_OF_DATA_FRAME[index_1]
            selected_df2 = LIST_OF_DATA_FRAME[index_2]
            # Récupérer les colonnes communes
            common_columns = set(selected_df1.columns).intersection(selected_df2.columns)
            # Créer une Combobox pour afficher les colonnes communes
            label_common_columns = tk.Label(df_dialogue, text="Colonnes communes :")
            label_common_columns.pack(pady=10, padx=10, anchor="w")
            common_columns_var = tk.StringVar()
            column_combobox3 = ttk.Combobox(df_dialogue,
                                            textvariable=common_columns_var,
                                            values=list(common_columns),
                                            width=30)  # Ajuster la largeur selon le contenu
            column_combobox3.pack(pady=(0, 5), padx=10)  # Ajout du padding uniquement en bas

            def combine_dataframe():
                common_column = common_columns_var.get()  # Retrieve the value of the StringVar
                df_combined = pd.merge(selected_df1, selected_df2, on=common_column, how="inner")
                LIST_OF_DATA_FRAME.append(df_combined)
                combined_name = f"combined_({dataframe_1})_({dataframe_2})"
                lb.insert(tk.END, combined_name)
                df_dialogue.destroy()

            combine_button = ttk.Button(df_dialogue, text="OK", command=combine_dataframe)
            combine_button.pack(pady=5)

        # Bouton OK
        ok_button = ttk.Button(df_dialogue, text="Choisir la colonne commune", command=choose_common_column)
        ok_button.pack(pady=5)

        # Centrer la fenêtre par rapport à la fenêtre principale (root)
        df_dialogue.transient(root)
        df_dialogue.grab_set()
        root.wait_window(df_dialogue)


# --------------------------------------------------------------------------------
# Dectection temporelle ----------------------------------------------------------
# --------------------------------------------------------------------------------
def detect_temporal_columns(df):
    temporal_columns = []
    for col in df.columns:
        # Vérifiez si le type de données est datetime64 ou si les valeurs sont dans un format temporel valide
        if pd.api.types.is_datetime64_any_dtype(df[col]) or all(isinstance(val, (dt, pd.Timestamp)) for val in df[col]):
            temporal_columns.append(col)
        elif df[col].dtype == "object":  # Vérifiez si le type de données est une chaîne de caractères
            # Essayez de convertir chaque valeur de la colonne en objet de date/heure
            try:
                if all(pd.to_datetime(val, errors="coerce") is not pd.NaT for val in df[col]):
                    temporal_columns.append(col)
            except ValueError:
                pass
    # Convertir les colonnes temporelles en timestamp
    for col in temporal_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
        # Proposer de renommer la colonne
        new_name = rename_temporal_column(column=col, df=df)
        if new_name:
            df.rename(columns={col: new_name}, inplace=True)
            temporal_columns.remove(col)
            temporal_columns.append(new_name)
    return temporal_columns


def rename_temporal_column(column, df):
    new_root = Tk()
    new_root.withdraw()
    example_value = df[column].iloc[0]  # Exemple de valeur de la colonne
    new_name = simpledialog.askstring("Renommer la colonne",
                                      f"Voulez-vous renommer la colonne temporelle '{column}' ?\nExemple de valeur : {example_value}\nEntrez un nouveau nom ou cliquez sur Annuler pour conserver le nom actuel:")
    new_root.destroy()
    return new_name


# --------------------------------------------------------------------------------
# Autres fonctions  --------------------------------------------------------------
# --------------------------------------------------------------------------------
def save_file(selected_df, file_name):
    # Ouvrir une boîte de dialogue pour enregistrer le fichier
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
                                             initialdir="/chemin/vers/le/dossier",
                                             initialfile=file_name)
    # Vérifier si un fichier a été sélectionné
    if file_path:
        # Enregistrer le DataFrame dans un fichier CSV à l'emplacement choisi
        selected_df.to_csv(file_path, index=False)


def save_new_dataframe(filepath, delimiter):
    df = pd.read_csv(filepath, delimiter=delimiter)
    df = df.dropna()
    temporal_columns = detect_temporal_columns(df)
    if temporal_columns:
        messagebox.showinfo("Information",
                            f"Les colonnes temporelles suivantes ont été détectées : {', '.join(temporal_columns)}")
    LIST_OF_DATA_FRAME.append(df)


def on_drop(event):
    file_paths = event.data.strip("{}").split("} {")
    print(file_paths)
    for file_path in file_paths:
        if '.csv' in file_path:
            LIST_OF_FILES.append(file_path)
            delimiter = detect_delimiter(file_path)
            save_new_dataframe(filepath=file_path, delimiter=delimiter)
            show_file_registered()
            lb.insert(tk.END, file_path.split("/")[-1])
        else:
            show_attention_message_box()


def rename_column_dialog(df, column_var):
    new_root = tk.Tk()
    new_root.withdraw()  # Masquer la fenêtre principale pendant que la boîte de dialogue est ouverte
    column_name = column_var.get()  # Nom de la colonne sélectionnée
    new_name = simpledialog.askstring("Renommer la colonne",
                                      f"Entrez un nouveau nom pour la colonne '{column_name}':",
                                      parent=new_root)  # Utiliser la fenêtre principale comme parent pour la boîte de dialogue
    new_root.destroy()  # Fermer la fenêtre après avoir obtenu le nouveau nom
    if new_name:
        df.rename(columns={column_name: new_name}, inplace=True)
        messagebox.showinfo("Information", f"La colonne '{column_name}' a été renommée en '{new_name}'.")
    else:
        messagebox.showinfo("Information", "Aucun nouveau nom spécifié.")


def describe_selected_column(df, column_var):
    selected_column = column_var.get()
    if selected_column:
        describe_window = tk.Toplevel(root)
        describe_window.title(f"Description de {selected_column}")

        # Création d'un widget Text pour afficher la description de la colonne
        text_widget = tk.Text(describe_window, wrap="word", height=10, width=50, selectbackground="blue")
        text_widget.insert("end", df[selected_column].describe())
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Ajout d'une barre de défilement pour le texte
        scroll_y = tk.Scrollbar(describe_window, orient="vertical", command=text_widget.yview)
        scroll_y.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scroll_y.set)

        # Ajuster la taille de la fenêtre de description en fonction du texte présent
        text_widget.update_idletasks()
        text_width = text_widget.winfo_reqwidth()
        text_height = text_widget.winfo_reqheight()
        describe_window.geometry(f"{text_width + 100}x{text_height + 50}")


def clean_dataframe(df, name, contamination_value):
    cols_to_include = []  # Colonnes à inclure
    for col in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df[col]):
            cols_to_include.append(col)
    df_filtered = df[cols_to_include]
    # Normalisation des données uniquement pour les colonnes non temporelles
    if len(df_filtered.columns) > 0:
        scaler = MinMaxScaler()
        df_normalized = pd.DataFrame(scaler.fit_transform(df_filtered), columns=df_filtered.columns)
        # Appliquer l'Isolation Forest sur les données normalisées
        outlier_detector = IsolationForest(contamination=contamination_value)  # Utiliser la valeur de contamination
        outliers = outlier_detector.fit_predict(df_normalized)
        # Filtrer les données en supprimant les valeurs aberrantes
        df_cleaned = df[outliers == 1]
        LIST_OF_DATA_FRAME.append(df_cleaned)
        cleaned_name = f"cleaned_({contamination_value})_({name})"
        lb.insert(tk.END, cleaned_name)
    else:
        messagebox.showinfo("Information", "Aucune colonne à nettoyer, veuillez sélectionner un autre DataFrame.")


def detect_delimiter(file_path):
    with open(file_path, "r") as file:
        first_line = file.readline()  # Lire la première ligne du fichier
        # Délimiteurs potentiels à tester
        delimiters = [',', ';', '\t', '|', ' ', ':']
        delimiter_counts = {delimiter: first_line.count(delimiter) for delimiter in delimiters}
        most_common_delimiter = max(delimiter_counts, key=delimiter_counts.get)
        return most_common_delimiter


# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# ------------------------------- GUI Setup -------------------------------------
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

root = TkinterDnD.Tk()
root.title("DataFrame Manager")
root.config(padx=50, pady=50)

canvas = Canvas(root, width=400, height=250, highlightthickness=0)
logo_path = "logo/8242984.png"
logo = PhotoImage(file=logo_path)
logo = logo.subsample(3)  # Redimensionner le logo
canvas.create_image(200, 120, image=logo)
canvas.create_text(200, 10, text='Visualiser et analyser vos fichiers ".csv"', font=('Arial', 12))

canvas.grid(row=0, column=0, columnspan=4, padx=20, pady=20)

label = tk.Label(root, text="Glissez vos fichiers ici")
label.grid(row=1, column=0, columnspan=2)

lb = tk.Listbox(root, width=50, height=20)  #
lb.drop_target_register(DND_FILES)
lb.dnd_bind('<<Drop>>', on_drop)
lb.grid(row=2, column=0, rowspan=8, columnspan=2)

btn_show_columns = ttk.Button(root, text="Afficher les colonnes", command=show_columns, width=25)
btn_show_columns.grid(row=2, column=2, padx=10, pady=5)

btn_rename_columns = ttk.Button(root, text="Renommer une colonne", command=rename_columns, width=25)
btn_rename_columns.grid(row=3, column=2, padx=10, pady=5)

btn_describe = ttk.Button(root, text="Afficher des statistiques", command=describe_selected_dataframe, width=25)
btn_describe.grid(row=4, column=2, padx=10, pady=5)

# Créer un bouton pour afficher le graphique
plot_button = ttk.Button(root, text="Afficher un graphique", command=plot_graph, width=25)
plot_button.grid(row=5, column=2, padx=10, pady=5)

btn_clean_columns = ttk.Button(root, text="Nettoyer la DataFrame", command=clean_df, width=25)
btn_clean_columns.grid(row=6, column=2, padx=10, pady=5)

btn_register = ttk.Button(root, text="Enregister la DataFrame", command=register_df, width=25)
btn_register.grid(row=7, column=2, padx=10, pady=5)

btn_combine = ttk.Button(root, text="Combiner des DataFrames", command=combination_selection, width=25)
btn_combine.grid(row=8, column=2, padx=10, pady=5)

btn_delete = ttk.Button(root, text="Supprimer la DataFrame", command=delete_selected_dataframe, width=25)
btn_delete.grid(row=9, column=2, padx=10, pady=5)  # Ajout de padx et pady pour l'espacement

root.mainloop()
