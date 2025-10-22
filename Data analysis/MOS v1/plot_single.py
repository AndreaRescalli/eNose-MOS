import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv("single_period_df.csv", header=3)

triangle_data = data[
    (data["Temperature Modulation"] == "Triangle")
    & (data.Sensor == "S-1")
    & (data.Repetition == 2)
    & (data.Concentration == 75)
    & (data.Compound == "BUT")
].reset_index()


fig, ax = plt.subplots()
x_values = np.arange(0, 1000)
ax2 = ax.twinx()
ax.plot(x_values, triangle_data.Data, "-")

triangle_values = [0.01 * x for x in range(500)]
triangle_values = np.append(triangle_values, [5 - 0.01 * x for x in range(500)])
ax2.plot(
    x_values,
    triangle_values,
    c="orange",
)

export_df = pd.DataFrame(
    {"x": x_values, "Triangle": triangle_data.Data, "Pattern": triangle_values}
)
export_df.to_csv("triangle.csv", index=False)

plt.show()

fig, ax = plt.subplots()
sq_tr = data[
    (data["Temperature Modulation"] == "Sq+Tr")
    & (data.Sensor == "S-4")
    & (data.Repetition == 3)
    & (data.Concentration == 130)
    & (data.Compound == "CH4")
].reset_index()

x_values = np.arange(0, 1000)
ax2 = ax.twinx()
ax.plot(x_values, sq_tr.Data, "-")

square_values = np.ones(int(1000 / 2) - 1) * 5
square_values = np.append(square_values, [0])
square_values = np.append(square_values, [0.02 * x for x in range(250)])
square_values = np.append(square_values, [5 - 0.02 * x for x in range(250)])
ax2.plot(
    x_values,
    square_values,
    c="orange",
)

plt.show()

export_df = pd.DataFrame({"x": x_values, "Sq+Tr": sq_tr.Data, "Pattern": square_values})
export_df.to_csv("sq_tr.csv", index=False)

triangle_data = data[
    (data["Temperature Modulation"] == "Triangle")
    & (data.Sensor == "S-1")
    & (data.Concentration == 75)
    & (data.Compound == "BUT")
].reset_index()

plt.plot(triangle_data.Data)
plt.show()
