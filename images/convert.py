# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPDF

# drawing = svg2rlg("mvc-classic.svg")
# renderPDF.drawToFile(drawing, "mvc5.pdf")


import cairosvg
cairosvg.svg2pdf(url='mvc-classic.svg', write_to='mvc6.pdf')
