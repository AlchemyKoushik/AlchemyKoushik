<div align="center">

<!-- Terminal-style animated profile README. Customize profile.json first. -->

<h3><code>koushik@github ~ $ ./contributions.sh</code></h3>

<img src="./contrib-heatmap.svg" width="860" alt="GitHub contribution graph, refreshed daily" />

<br><br>

<h3><code>koushik@github ~ $ whoami</code></h3>

<table>
<tr>
<td valign="top"><img src="./profile-ascii.svg" width="420" alt="ASCII portrait" /></td>
<td valign="top"><img src="./stats.svg" width="420" alt="Contribution streak and statistics" /></td>
</tr>
</table>

<br><br>

<h3><code>koushik@github ~ $ ./links.sh</code></h3>

<p><b>Business Intelligence and Automation Expert</b></p>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-profile-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/koushik-bhandary-ai)
[![Personal Email](https://img.shields.io/badge/Personal_Email-contact-ea4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:koushiknox@gmail.com)
[![Work Email](https://img.shields.io/badge/Work_Email-contact-ea4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:koushik.bhandary@alchemy-research.com)

<br>

</div>

## Local setup

1. Edit [`profile.json`](./profile.json) with your GitHub username, display name, terminal handle, and photo filename.
2. Put your portrait at the repository root using that filename. A well-lit, high-contrast photo works best.
3. Install dependencies and generate the portrait:

   ```bash
   python -m pip install -r scripts/requirements-photo.txt
   python scripts/prep_photo.py source-photo.jpg source-prepped.png
   python scripts/make_ascii_svg.py source-prepped.png profile-ascii.svg
   ```

4. Fetch your contribution data and render the live cards:

   ```bash
   python scripts/fetch_contributions.py
   python scripts/render_heatmap_svg.py
   python scripts/render_stats_svg.py
   ```

The GitHub Action in [`.github/workflows/update-profile-art.yml`](./.github/workflows/update-profile-art.yml) repeats the data fetch and SVG rendering daily. It uses GitHub’s public contribution HTML endpoint, so no personal access token is required.
