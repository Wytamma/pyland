import click
from jinja2 import FileSystemLoader, Environment, Template
import os
import subprocess
from PIL import Image


def _load_template(name):
    templateLoader = FileSystemLoader([os.path.join(os.path.dirname(__file__)), "./"])
    templateEnv = Environment(
        loader=templateLoader, trim_blocks=True, lstrip_blocks=True
    )
    return templateEnv.get_template(name)


def _generate_icons(image_path, outputfolder="."):
    icon_sizes = [
        "android-chrome-192x192.png",
        "android-icon-144x144.png",
        "apple-icon-120x120.png",
        "apple-icon-76x76.png",
        "android-icon-192x192.png",
        "apple-icon-144x144.png",
        "android-icon-36x36.png",
        "apple-icon-152x152.png",
        "ms-icon-144x144.png",
        "android-icon-48x48.png",
        "apple-icon-180x180.png",
        "ms-icon-150x150.png",
        "android-icon-72x72.png",
        "apple-icon-57x57.png",
        "favicon-16x16.png",
        "ms-icon-310x310.png",
        "android-icon-96x96.png",
        "apple-icon-60x60.png",
        "favicon-32x32.png",
        "ms-icon-70x70.png",
        "apple-icon-114x114.png",
        "apple-icon-72x72.png",
        "favicon-96x96.png",
    ]

    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)

    img = Image.open(image_path)
    for icon_size in icon_sizes:
        click.echo(icon_size)
        size = int(icon_size.split("-")[-1].split("x")[0])
        resized_img = img.resize((size, size), Image.ANTIALIAS)
        resized_img.save(f"{outputfolder}/{icon_size}", format="PNG")
    # speical
    click.echo("favicon.ico")
    resized_img = img.resize((16, 16), Image.ANTIALIAS)
    resized_img.save(f"{outputfolder}/favicon.ico")
    resized_img = img.resize((192, 192), Image.ANTIALIAS)
    click.echo("apple-icon.png")
    resized_img.save(f"{outputfolder}/apple-icon.png", format="PNG")
    # files
    with open("Failed.py", "w") as file:
        file.write("whatever")


@click.group()
def cli():
    """A simple command line tool for generating and deploying landing pages."""
    pass


@cli.command()
@click.argument("url")
@click.option("--title", default="TITLE", help="Title of landing page")
@click.option("-t", "--template", help="Template to render")
@click.option("-l", "--logo", help="Path to logo image")
@click.option("-d", "--description", help="Description of landing page")
@click.option(
    "-bg", "--background", help="Background image for landing page (template dependent)"
)
def generate(url, title, template, description, logo, background):
    """Generates a static landing page."""
    path = f"./{url}"

    if not os.path.exists(path):
        os.mkdir(path)

    if not template:
        template = "templates/template1.html"  # choice
    template = _load_template(template)

    with open(f"{path}/index.html", "w") as file:
        file.write(template.render(title=title, description=description, logo=logo))

    if logo:
        _generate_icons(logo, outputfolder=path)
        with open(f"{path}/manifest.json", "w") as file:
            file.write(_load_template("templates/manifest.json.jinja").render(name=url))
        with open(f"{path}/browserconfig.xml", "w") as file:
            file.write(
                """<?xml version="1.0" encoding="utf-8"?><browserconfig><msapplication><tile><square70x70logo src="/ms-icon-70x70.png"/><square150x150logo src="/ms-icon-150x150.png"/><square310x310logo src="/ms-icon-310x310.png"/><TileColor>#ffffff</TileColor></tile></msapplication></browserconfig>"""
            )


@cli.command()
@click.argument("url")
@click.option("-p", "--path", help="Path to site")
@click.option("-r", "--region", default="ap-southeast-2", help="Region to deploy in")
def deploy(url, path, region):
    """Deploys the website to AWS S3 (depends on s3-website cli)"""
    if not path:
        path = url
    s3_command = f"s3-website create -r {region} -u . -d {url}"
    print(s3_command)
    process = subprocess.Popen(s3_command.split(), stdout=subprocess.PIPE, cwd=path)
    output, error = process.communicate()
    if error:
        print("An error while deploying:", error)
    else:
        print(output.decode("utf-8").split("Updated config file: .s3-website.json")[-1])


@cli.command()
@click.argument("filename")
@click.option("-o", "--out", default="./", help="Output folder for icons")
def logo(filename, out):
    _generate_icons(filename, out)


if __name__ == "__main__":
    cli()
