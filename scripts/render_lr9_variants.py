"""Render newly authored formula samples; requires matplotlib (pip install matplotlib)."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]/'moodle/lr9'
variants=json.loads((root/'variants_16_31.json').read_text())
for number,formulas in variants.items():
    fig=plt.figure(figsize=(12,4.4),dpi=180,facecolor='white')
    for i,formula in enumerate(formulas):
        fig.text(.035,.79-i*.29,'$'+formula+'$',fontsize=19,va='center')
    fig.savefig(root/'generated'/f'variant_{number}.png',bbox_inches='tight',pad_inches=.25)
    plt.close(fig)
print(f'Rendered {len(variants)} variants, {sum(map(len,variants.values()))} formulas')
