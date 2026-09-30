# Dam stability classroom tools

Two calculation tools in one app:

1. **Earthfill / rockfill (Bishop)** — circular-slip Bishop analysis of a homogeneous earthfill dam, an earthfill dam with a clay core, and a rockfill dam with a concrete face (CFRD).
2. **Concrete gravity dam** — overturning, sliding, foundation bearing and heel tension for a triangular gravity section.

Choose the tool at the top, set the inputs, then press **Run analysis**. The plot and safety checks appear on the right.

Units: lengths in m, unit weights in kN/m³, stresses and cohesion in kPa.

## Students — open in the browser

Once the instructor has deployed the app, use the Streamlit URL they share. No Python install is required.

Source repository: [https://github.com/ingjpal/dam-bishop-stability](https://github.com/ingjpal/dam-bishop-stability)

## Run on your own computer

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at [http://localhost:8501](http://localhost:8501).

Bishop grid search is slower than a single circle (often one to a few minutes). The gravity-dam check is immediate.

## Instructor — publish a URL for the class

1. Push this repository to GitHub (public).
2. Go to [https://share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **New app** → select this repo → main file `app.py` → Deploy.
4. Share the `*.streamlit.app` link with students.

Calculation engines: `earthfill_dam_bishop.py` and `gravity_dam.py`. Interface: `app.py`.

Short student manuals (also shown in the app under **Help**):

- [help_bishop.md](help_bishop.md) — earthfill / rockfill Bishop analysis
- [help_gravity.md](help_gravity.md) — concrete gravity dam checks
