
# Making Persistence diagram/barcode for RRM by GRRM

This project is the method described in the paper [Reconstructing Reaction Pathways Using the GRRM Program](https://pubs.acs.org/doi/full/10.1021/acs.jctc.2c01204).

## Prerequisites

To run this project, you need to install the following:

- **Python** (version 3.5 or later)
  - Libraries: `numpy`, `matplotlib`, `homcloud`

## Installation

Clone the repository:

```sh
git clone https://github.com/mochimochi-brian/GRRM-PD.git
```

Navigate to the project directory:

```sh
cd GRRM-PD
```

Install the required Python libraries:

```sh
pip install numpy matplotlib homcloud
```

## Usage

To execute the program, run the following command in the project directory:

```sh
python MKPD.py *EQ_list.log *TS_list.log
```

