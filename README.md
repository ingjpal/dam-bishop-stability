# Dam slope stability (Bishop simplified)

Classroom app for circular-slip Bishop analysis of:

- a homogeneous earthfill dam
- an earthfill dam with a clay core
- a rockfill dam with a concrete face (CFRD)

Set the water condition, choose a single trial circle or a grid search, edit geometry and materials, then press **Run analysis**. The plot and factor of safety appear on the right.

Units: lengths in m, unit weights in kN/m³, cohesion in kPa.

## Students — open in the browser

Once the instructor has deployed the app, use the Streamlit URL they share. No Python install is required.

## Run on your own computer

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at [http://localhost:8501](http://localhost:8501).

Grid search is slower than a single circle (often one to a few minutes).

## Instructor — publish a URL for the class

1. Push this repository to GitHub (public).
2. Go to [https://share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **New app** → select this repo → main file `app.py` → Deploy.
4. Share the `*.streamlit.app` link with students.

The calculation engine is `earthfill_dam_bishop.py`. The interface is `app.py`.
