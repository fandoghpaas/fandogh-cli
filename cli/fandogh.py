#!/usr/bin/env python
import click

@click.group("cli")
def cli():
    pass


@click.group("app")
def app():
    pass


@click.group("container")
def container():
    pass


cli.add_command(app)
cli.add_command(container)


@click.command()
@click.option('--name', prompt='application name', help='your application name')
def init(name):
    click.echo('Initialized the ' + name)


app.add_command(init)


@cli.command()
def dropdb():
    click.echo('Dropped the database')


if __name__ == '__main__':
    cli()
