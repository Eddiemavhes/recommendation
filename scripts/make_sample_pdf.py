from reportlab.pdfgen import canvas
from pathlib import Path
p = Path('scripts/sample_cv.pdf')
if not p.parent.exists():
    p.parent.mkdir(parents=True)
c = canvas.Canvas(str(p))
c.drawString(100,750,'John Doe')
c.drawString(100,735,'Experienced Python Developer with 5 years of experience')
c.drawString(100,720,'Skills: Python, Django, SQL')
c.save()
print('Created', p)
