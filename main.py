from tkinter import *
from tkinter.filedialog import askopenfilename

from model.config import Configuration
from view.graphs import *

configuration = Configuration()


def onselect(xmin, xmax):
    global _start
    global _end
    indmin, indmax = np.searchsorted(x, (xmin, xmax))
    indmax = min(len(x) - 1, indmax)

    # thisx = x[indmin:indmax]
    # thisy = y[indmin:indmax]
    _start = indmin
    _end = indmax


def sel(event):
    print(event)
    # print(scale.get)


def select_file():
    configuration.setFileName(askopenfilename(filetypes=[("Garmin fit files", "*.fit")]))


def analyze_data():
    value = variable.get()
    if value == "Heart Rate":
        df = configuration.getFitData()

        if df is not None:
            plot_hr(df)
    if value == "Heart Rate + Power":
        df = configuration.getFitData()
        if df is not None:
            plot_hrpwr(df)
    if value == "DFA Alpha1":
        features_df = configuration.getHRVData(master)
        print(round(np.mean(features_df['alpha1']), 2))

        ax = plot_multi(features_df, x='timestamp', y='alpha1 heartrate'.split(), figsize=(22, 10))
        plt.grid()
        plt.show()
    if value == "Heart Rate vs DFA Alpha1":
        features_df = configuration.getHRVData(master)
        plt.scatter(features_df['heartrate'], features_df['alpha1'])

        # Calculate the Trendline
        features_df = features_df.dropna(subset=["alpha1"])
        z = np.polyfit(features_df['heartrate'], features_df['alpha1'], 1)
        p = np.poly1d(z)

        # Display the Trendline
        plt.plot(features_df['heartrate'], p(features_df['heartrate']), color="red", linewidth=2, linestyle="--")

        # Display the Trendline
        #plt.plot(x, df['alpha1'])

        plt.grid()
        plt.show()


if __name__ == '__main__':
    global _start
    global _end
    global var

    x = 1

    # scale = Scale(root, from_=10, to=20, orient=HORIZONTAL, command=sel)
    # scale.pack(anchor=CENTER)

    OPTIONS = [
        "Heart Rate",
        "Heart Rate + Power",
        "Zones",
        "DFA Alpha1",
        "Heart Rate vs DFA Alpha1"
    ]  # etc

    master = Tk()

    variable = StringVar(master)
    variable.set(OPTIONS[0])  # default value

    w = OptionMenu(master, variable, *OPTIONS)
    w.pack()

    button1 = Button(master, text="Show Graph", command=analyze_data)
    button1.pack()

    open_button = Button(
        master,
        text='Open a Fit File',
        command=select_file
    )
    open_button.pack(expand=False)

    button2 = Button(master, text="Exit", command=exit)
    button2.pack()

    mainloop()
