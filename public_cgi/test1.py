#!/usr/bin/env python3

import cgi
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import base64
from io import BytesIO
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


form = cgi.FieldStorage()
form_input = (form.getfirst('W', None), form.getfirst('Q2', None), form.getfirst('Cos(theta)', None))
input_data = ()
none_counter = 0
try:
    for i in form_input:
        if i is None:
            none_counter += 1
        else:
            j = float(i.replace(',', '.'))
            if i == form_input[0]:
                if j < 1.11 or j > 2.01:
                    raise TypeError
                else:
                    input_data += ('W', j)
            if i == form_input[1]:
                if j < 0.3 or j > 4.16:
                    raise TypeError
                else:
                    input_data += ('Q2', j)
                    pass
            if i == form_input[2]:
                if j < -1 or j > 1:
                    raise TypeError
                else:
                    input_data += ('Cos(theta)', j)
        if none_counter == 2:
            raise ZeroDivisionError
except ZeroDivisionError:
    print(error_html('Not enough data'))
except ValueError:
    print(error_html('Incorrect data entry'))
except TypeError:
    print(error_html('Incorrect values entered'))
else:

    def name_with_unit(name):
        for i in range(3):
            if name == 'W':
                return 'W, GeV'
            elif name == 'Q2':
                return r'$Q^2, GeV^2$'
            else:
                return r'$Cos(\theta)$'

    def error_html(text):
        return f'''Content-type: text/html\n
                    <!DOCTYPE HTML>
                    <html>
                            <head>
                                    <meta charset="utf-8">
                                    <title>Error</title>
                            </head>
                            <body style="text-align: center; padding-top: 20%;">
                            <form action="https://clas.sinp.msu.ru/~stanislavsorokin/">
                            Error! {text} <br>
                            <input type="submit" value="Re-enter" style="margin-top: 15px">
                            </body>
                    </html>'''
    #   LINK REPLACMENT: https://clas.sinp.msu.ru/~stanislavsorokin/ , http://localhost:8888/

    f_units = [r'$\frac{d\sigma_{t}}{d\Omega_{\pi}}, \frac{mcb}{sr}$',
                    r'$\frac{d\sigma_{l}}{d\Omega_{\pi}}, \frac{mcb}{sr}$',
                    r'$\frac{d\sigma_{tt}}{d\Omega_{\pi}}, \frac{mcb}{sr}$',
                    r'$\frac{d\sigma_{lt}}{d\Omega_{\pi}}, \frac{mcb}{sr}$']

    df = pd.read_csv(r'final_table2.csv',
                             header=None, sep='\t',
                             names=['Channel', 
                                    'Sigma_T', 'dSigma_T', 'Sigma_L', 'dSigma_L',
                                    'Sigma_TT', 'dSigma_TT', 'Sigma_LT', 'dSigma_LT',
                                    'W', 'Q2', 'Cos(theta)'])
    # REPLACEMENT: r'C:\Users\ssoro\Documents\FoP\Dev\cgi-bin\final_table2.csv' , final_table2.csv

    channel = form.getfirst('channel_select')
    name1 = input_data[0]
    value1 = input_data[1]
    name2 = input_data[2]
    value2 = input_data[3]
    for i in ['W', 'Q2', 'Cos(theta)']:
        if i != input_data[0] and i != input_data[2]:
            NAME_3 = i

    N = 50

    fig = plt.figure(figsize=[17, 8], tight_layout=True)
    if channel == 'pin':
        df = df[(df.Channel == 8) | (df.Channel == 14) | (df.Channel == 41) | (df.Channel == 141)].reset_index()
        fig.suptitle(r'$\gamma_{v}p \rightarrow \pi^{+}n$', size=20, y=1)
    elif channel == 'pi0p':
        df = df[(df.Channel == 9) | (df.Channel == 37) | (df.Channel == 170)].reset_index()
        fig.suptitle(r'$\gamma_{v}p \rightarrow \pi^{0}p$', size=20, y=1)
    else:
        print('ERROR!!! channel')
    points = (df[name1].values, df[name2].values, df[NAME_3])
    xi = (np.array([value1 for i in range(N)]), np.array([value2 for i in range(N)]), np.linspace(min(df[NAME_3].values.tolist()), max(df[NAME_3].values.tolist()), N))
    f_sigma = griddata(points, df['Sigma_T'].values, xi, method='linear')
    axs = fig.subplots(2, 2)
    x_label = name_with_unit(NAME_3)
    for ax, yy, yy_err, f_label in zip(axs.flat, ['Sigma_T', 'Sigma_L', 'Sigma_TT', 'Sigma_LT'], ['dSigma_T', 'dSigma_L', 'dSigma_TT', 'dSigma_LT'], f_units):
        f_sigma = griddata(points, df[yy].values, xi, method='linear')
        f_err_sigma = griddata(points, df[yy_err].values, xi, method='linear')
        ax.errorbar(x=xi[2], y=f_sigma, yerr=f_err_sigma, marker='s', linestyle='solid', color='black',
                            markersize=5, linewidth=2, ecolor='#ff6666', elinewidth=1, capsize=2)
        ax.minorticks_on()
        ax.grid(True, which='major', linestyle='-.')
        ax.set_xlabel(x_label, fontsize=20)
        ax.set_ylabel(f_label, fontsize=25)
        ax.tick_params(axis='both', which='both', direction='in', labelsize=12)
    fig.subplots_adjust(hspace=8, wspace=20)
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')    

    print('''Content-type: text/html\n
            <!DOCTYPE HTML>
            <html>
                    <head>
                            <meta charset="utf-8">
                            <style>
                                .submit_container {
                                    text-align: center;
                                }
                                .submit_container>input {
                                    padding: 7px;
                                    background-color: white;
                                    font-weight: bold;
                                    font-size: 18px;
                                }
                            </style>
                            <title>Graph</title>
                    </head>
                    <body>
                    <form action="https://clas.sinp.msu.ru/~stanislavsorokin/">''')
    print('<img src=\'data:image/png;base64,{}\'>'.format(encoded))
    print('''<div class="submit_container"><input type="submit" value="Re-enter"></div>
                    </body>
            </html>
    ''')