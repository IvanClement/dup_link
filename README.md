# dup_link
A python script to delete duplicates files, and replace those with links (hard or soft).
By default, creates hardlinks. Soft links if hard links can't be created

One of my very first python script.
Still ugly.

Needs to be commented....

# requirements:
* packages:
    - python3
    - python3-pip
* modules:
    - pip3 install tqdm
    or
    - pip3 install --user tqdm

# Installation:
* download dup_link.py
* execute following commands:
    - sudo mv dup_link.sh /usr/local/bin
    - sudo chown root:root /usr/local/bin/dup_link.sh
    - sudo chmod +x /usr/local/bin/dup_link.sh