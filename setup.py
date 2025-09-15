#!/usr/bin/env python3
"""
📦 SETUP.PY - SIMULADOR DE CICLORUTAS 📦

Archivo de configuración para la instalación del paquete.

Autor: Sistema de Simulación de Ciclorutas
Versión: 2.0 (Refactorizado)
"""

from setuptools import setup, find_packages
import os

# Leer el README para la descripción larga
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Leer requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="simulador-ciclorutas",
    version="2.0.0",
    author="Sistema de Simulación de Ciclorutas",
    author_email="contacto@ciclorutas.com",
    description="Simulador avanzado de ciclorutas con interfaz gráfica",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/usuario/ciclorutas",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "ciclorutas=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="simulation, cycling, transportation, network, graph, tkinter, matplotlib",
    project_urls={
        "Bug Reports": "https://github.com/usuario/ciclorutas/issues",
        "Source": "https://github.com/usuario/ciclorutas",
        "Documentation": "https://ciclorutas.readthedocs.io/",
    },
)
