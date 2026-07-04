from setuptools import find_packages,setup
from typing import List

def get_requiremnts()->list[str]:
    """

    this function retutn the list of requirements
    
    """  
    requiremnt_lst:list[str]=[]
    try:
        with open("requirements.txt","r") as file:
            #read line from the file 
            lines=file.readlines()
            # process each line 
            for line in lines:
                requiremnt=line.strip()
                #ignore empty line
                if requiremnt and requiremnt!= "-e .":
                    requiremnt_lst.append(requiremnt)
    except FileNotFoundError:
        print("requiremnt.txt file not found")

    return requiremnt_lst

# print(get_requiremnts())

setup(
name="NetworkSecurity",
version="0.0.1",
author="jai kumar",
author_email="kumarjai9850@gmial.com",
packages=find_packages(),
install_requires=get_requiremnts()
) 