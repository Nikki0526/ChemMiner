#pip install openai==1.3.7

from openai import OpenAI

client = OpenAI(
    base_url="https://oneapi.xty.app/v1",
    api_key="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
)

# prepare package loading

import openai
import pandas as pd
import json
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, colors
from pandas.core.frame import DataFrame
from tqdm import tqdm
import time
from google.colab import drive
import os
import json
import ast
import base64
import re
import glob

drive.mount('/content/drive')
os.chdir("/content/drive/MyDrive")

os.chdir("/content/drive/MyDrive/Colab Notebooks/research/Bayesian Optimization/GPT/final")

# initialize functions

def text_length(start,end,input):
  length = 0
  for i in range(end-start+1):
    length += len(input[start+i])
  return length

def merge(start,end,key_index,input):
  if start == key_index:
    merge_result = []
    bar = 3000
  else:
    merge_result = [key_index]
    bar = 3000 - len(input[key_index])

  for j in range(end-start):
    if text_length(start,start+j,input) < bar:
      merge_result.append(start+j)

    if text_length(start,start+j,input) >= bar:
      break

  return merge_result, start+j

def prompt_function_gpt4_1v1(content):
  completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[{"role": "system", "content": "You are a helpful assistant on chemistry."},
    {"role": "user", "content": '''
    I am providing a paragraph from a piece of chemical literature. I would like you to help me identify instances of coreference, where a full chemical name is immediately followed by a shorthand label or alias. Here is the paragraph:

    "Tetraethyl (E)-8,9-Bis((Z)-3-ethoxy-3-oxo-2-phenylprop-1-en-1-
yl)hexadeca-1,8,15-triene-6,6,11,11-tetracarboxylate, 7c. It was
obtained from 3n (25 mg, 0.06 mmol) following the general
procedure for cycloisomerization reactions with Cp*RuCl(cod) and
purified by flash column chromatography (Hexane/AcOEt, 19:1).
Colorless oil (22 mg, 0.03 mmol, 86%);"

    Please provide the coreference in the following json format:
    {<full chemical name>: {<shorthand label or alias>}}
    Pay attention to direct aliases that come immediately after the chemical names.
    '''},
    {"role": "assistant", "content":
    '''
    {
      "Tetraethyl (E)-8,9-Bis((Z)-3-ethoxy-3-oxo-2-phenylprop-1-en-1-yl)hexadeca-1,8,15-triene-6,6,11,11-tetracarboxylate": "7c"
    }
    '''},
    {"role": "user", "content": f'''I am providing a paragraph from another piece of chemical literature. Same as before, I would like you to help me identify instances of coreference, where a full chemical name is immediately followed by a shorthand label or alias.
    Here is the paragraph:  '{content}', Please provide the coreference in the same json format as before. Pay attention to direct aliases that come immediately after the chemical names.
    If there do not exist such coreference, please tell me "No coreference". Please check carefully about the full chemical name and shorthand label. The total number of coreference should be smaller than 5.
    '''}
  ],
  temperature=0.2,
        stream=True
)
  return completion

def prompt_function_general_procedure(content):
  completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[{"role": "system", "content": "You are a helpful assistant on chemistry."},
    {"role": "user", "content": '''Experimental Procedures and Characterization of Products.
General Procedure for the Preparation of Products.
[Ni2(iPr2Im)4(μ-COD)] (0.1 mmol, 83 mg), CsF (2 mmol, 304
mg), Ar-Bneop (2 mmol), fluoroarene, and toluene (10 mL) were
added to a Schlenk tube equipped with a magnetic stirring bar. The
reaction mixture was heated at 100 °C for 18 h, and after that H2O (5
mL) was added. The product was extracted with EtOAc (3 × 20 mL),
and then the combined organic layers were dried over Na2SO4 and
filtered, and the volatiles were removed in vacuo. The product was
purified by column chromatography on silica gel using hexane as the
eluent. The solvent of the product-containing fraction of the eluent
was evaporated in vacuo. The yields provided are based on Ar-Bneop.
Spectroscopic Data of the Products. 2,3,4,5,6-Pentafluoro-1,1′-
biphenyl (3aa). Following the general procedure, a white solid in 72%
yield (351 mg) was obtained from C6F6 (4 mmol, 462 μL) and C6H5-
Bneop (2 mmol, 380 mg). 1H NMR (500 MHz, CDCl3) δ 7.52−7.45
(m, 3 H), 7.44−7.41 (m, 2 H); 13C{1H} NMR (125 MHz, CDCl3) δ
144.2 (d of m, 1JCF = 247.3 Hz), 140.4 (d of m, 1JCF = 253.7 Hz),
137.8 (d of m, 1JCF = 250.9 Hz), 130.1 (t, 3JCF = 1.5 Hz), 129.3, 128.7,
126.4, 115.9 (m); 19F NMR (470 MHz, CDCl3) δ −143.26 (m, 2 F),
−155.65 (t, J = 21.0 Hz, 1 F), −162.27 (m, 2 F); 19F{1H} NMR (188
MHz, CDCl3) δ −143.28 (dd, J = 8.1, 22.0 Hz, 2 F), −155.68 (t, J =
21.0 Hz, 1 F), −162.31 (td, J = 8.1, 22.0 Hz, 2 F); HRMS (ASAP)
[C12H5F5] calcd 244.0306, found 244.0305.
Spectroscopic data for 3aa match with those previously reported in
the literature.3k
2,3,4,5,6-Pentafluoro-4′-methyl-1,1′-biphenyl (3ab). Following
the general procedure, a white solid in 76% yield (390 mg) was
obtained from C6F6 (4 mmol, 462 μL) and 4-CH3-C6H4-Bneop (2
mmol, 408 mg). 1H NMR (500 MHz, CDCl3) δ 7.31 (m, 4 H), 2.42
(s, 3 H); 13C{1H} NMR (125 MHz, CDCl3) δ 144.2 (d of m, 1JCF =
247.7 Hz), 140.2 (d of m, 1JCF = 253.3 Hz), 139.4, 137.8 (d of m, 1JCF
= 250.7 Hz), 130.0, 129.5, 123.4, 115.9 (m), 21.4; 19F NMR (470
MHz, CDCl3) δ −143.37 (m, 2 F), −156.15 (t, J = 18.8 Hz, 1 F),
−162.46 (m, 2 F); 19F{1H} NMR (188 MHz, CDCl3) δ −143.39 (dd,
J = 8.1, 22.8 Hz, 2 F), −156.17 (t, J = 21.0 Hz, 1 F), −162.50', could you please help me extract the information of yield/reactant/reagent/solvent/product from each reaction in the previous content in json format?
The content usually includes a general procedure, followed by the specific description of the reaction. The extraction should take into account both the general procedure, which provides the overall context, and the specific descriptions of each reaction, which offer unique details.
When a piece of information is missing from the specific description, consider the general procedure to infer the missing details. However, if there is any conflicting information, the specific description should take precedence.
    '''},
    {"role": "assistant", "content":
    '''
    {"1": {"yield": "72%(351 mg)","reactant": "C6F6(4 mmol, 462 μL),C6H5-Bneop(2 mmol, 380 mg),fluoroarene","reagent": "[Ni2(iPr2Im)4(μ-COD)](0.1 mmol, 83 mg),CsF(2 mmol, 304 mg)","solvent": "toluene(10 mL)","product": "2,3,4,5,6-Pentafluoro-1,1ʹ-biphenyl"},
    "2": {"yield": "76%(390 mg)","reactant": "C6F6(4 mmol, 462 μL),4-CH3-C6H4-Bneop(2 mmol, 408 mg),fluoroarene ","reagent": "[Ni2(iPr2Im)4(μ-COD)](0.1 mmol, 83 mg),CsF(2 mmol, 304 mg)","solvent": "toluene(10 mL)","product": "2,3,4,5,6-Pentafluoro-4′-methyl-1,1′-biphenyl"}
    }
    '''},
    {"role": "user", "content": f'''From the following contents: '{content}', could you please help me extract the information of yield/reactant/reagent/solvent/product from each reaction in the previous content in json format?
    The content usually includes a general procedure, followed by the specific description of the reaction. The extraction should take into account both the general procedure, which provides the overall context, and the specific descriptions of each reaction, which offer unique details.
    When a piece of information is missing from the specific description, consider the general procedure to infer the missing details. However, if there is any conflicting information, the specific description should take precedence.

    Please provide the chemical reaction details formatted as a JSON object. The structure must strictly adhere to the following requirements:
    1.The JSON object should consist exclusively of these keys: "yield", "reactant", "reagent", "solvent", and "product".
    2.If yield information is not available, the value for the "yield" key should be "No specific information about yield".
    3.The response should be clean and precise: it must not contain ellipses ("..."), backticks ("`"), or any code block identifiers such as "```json".
    Please ensure the JSON object is properly formatted with no additional characters or elements outside of the specified structure.
    '''}
  ],
        stream=True
)
  return completion


IMAGE_EXTS = (".png", ".jpg", ".jpeg")

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extract_json_content(message: str) -> str:
    match = re.search(r"\{.*\}", message, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON content found in the message!")

def prompt_function_figure_abbrev(image_path: str,
                                 text_prompt: str = '''
Analyze the provided image and extract all the abbreviations (e.g., 1a, 2b, L1, B1, S1, etc.) and their corresponding chemical compound names in English.
Organize the extracted information into a structured JSON format. Each abbreviation should be used as a key, and its full chemical name should be the value.
Ensure that all data is accurate and properly formatted. For example:
{
  "1a": "2-Chloroquinoline",
  "B1": "Potassium carbonate",
  "S1": "EtOH/H2O (9:1)"
}
Focus on clarity, consistency, and completeness, extracting all abbreviations and their corresponding full chemical names based on the molecular structures shown in the image.
''',
                                 model: str = "gpt-4-vision-preview",
                                 max_tokens: int = 1000) -> dict:

    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=max_tokens,
    )

    return_message = response.choices[0].message.content or ""
    cleaned_message = extract_json_content(return_message)
    data = json.loads(cleaned_message)

    if not isinstance(data, dict):
        raise ValueError(f"Vision output is not a JSON object. Got: {type(data)}")

    normalized = {}
    for k, v in data.items():
        if k is None:
            continue
        kk = str(k).strip()
        vv = "" if v is None else str(v).strip()
        if kk:
            normalized[kk] = vv

    return normalized

def find_paper_images(paper_id: str, image_root: str) -> list:
    pid = str(paper_id)
    folder = os.path.join(image_root, pid)

    if not os.path.isdir(folder):
        return []

    files = []
    for ext in IMAGE_EXTS:
        files.extend(glob.glob(os.path.join(folder, f"*{ext}")))
        files.extend(glob.glob(os.path.join(folder, f"*{ext.upper()}")))
    return sorted(set([p for p in files if p.lower().endswith(IMAGE_EXTS)]))

success_list_cor = []
success_list_react = []
total_number = 0
paper_number = 0
IMAGE_ROOT = "/content/drive/MyDrive/Colab Notebooks/research/Bayesian Optimization/GPT/figure_and_table/literature"

with open('/content/drive/MyDrive/Colab Notebooks/research/Bayesian Optimization/GPT/1900/scihub(doi).jsonl', 'r', encoding="utf-8") as f:
  for line in f:
    data = json.loads(line)
    total_number += 1

    paper_id = data['meta']['id']
    paper_number+=1
    print('-------------',paper_number,'-------------')

    '''
    paper_images = find_paper_images(paper_id, IMAGE_ROOT)
    print(f"[paper {paper_id}] found {len(paper_images)} image(s)")

    merged_abbrev_map = {}   # abbr -> name OR list[name] if conflicts
    per_image_records = []   # optional: keep per-image raw map for debugging

    for img_path in paper_images:
        try:
            img_map = prompt_function_figure_abbrev(img_path)
            per_image_records.append({
                "paper_id": str(paper_id),
                "image_file": os.path.basename(img_path),
                "map": img_map
            })

            # merge into merged_abbrev_map with conflict-handling
            for abbr, name in img_map.items():
                if abbr not in merged_abbrev_map:
                    merged_abbrev_map[abbr] = name
                else:
                    existing = merged_abbrev_map[abbr]
                    if existing == name:
                        continue
                    # if conflict: store as list
                    if isinstance(existing, list):
                        if name not in existing:
                            existing.append(name)
                    else:
                        merged_abbrev_map[abbr] = [existing, name]

            time.sleep(2)

        except Exception as e:
            print(f"[paper {paper_id}] error processing image: {img_path} -> {e}")

    # write per-paper outputs (JSON + CSV)
    if len(merged_abbrev_map) > 0:
        # JSON
        with open(f"GPT_output_fig_abbrev_{paper_id}.json", "w", encoding="utf-8") as wf:
            json.dump(merged_abbrev_map, wf, ensure_ascii=False, indent=2)

        # CSV (flatten)
        rows = []
        for abbr, name in merged_abbrev_map.items():
            if isinstance(name, list):
                for n in name:
                    rows.append({"paper_id": str(paper_id), "abbreviation": abbr, "chemical_name": n})
            else:
                rows.append({"paper_id": str(paper_id), "abbreviation": abbr, "chemical_name": name})

        pd.DataFrame(rows).to_csv(f"GPT_output_fig_abbrev_{paper_id}.csv", index=False)

        print(f"[paper {paper_id}] saved figure abbrev map -> GPT_output_fig_abbrev_{paper_id}.json/.csv")
    else:
        print(f"[paper {paper_id}] no abbrev map extracted from images")
    '''

    content_str = data['text'] # Extract the paper text content

    a = content_str.split(".\n") # Split by line breaks (only those that occur at sentence boundaries)

    for i in range(len(a)): # Add back the '.\n' that was removed in the previous split step
      a[i] += '.\n'

    key_index = []
    for i in range(len(a)):
      if a[i].find("General Procedure") != -1: # Case-insensitive match for 'general procedure'
        #number.append(txt_list[k])
        #print(txt_list[k])
        key_index.append(i)

      if a[i].find("Typical Procedure") != -1: # Case-sensitive match for 'Typical Procedure'
        #print(a[i])
        key_index.append(i)
        #number.append(txt_list[k])
      if a[i].find("General Experimental Procedure") != -1: # Case-sensitive match for 'General Experimental Procedure'
        #print(a[i])
        key_index.append(i)
        #number.append(txt_list[k])

    if len(key_index) == 0:
      continue # If 'general procedure' never appears, skip to the next paper

    # Merge sections by length to form GPT input sections
    section_list = []
    for i in range(len(key_index)):
      if i < len(key_index) - 1: # For non-last key_index, take the sentences between adjacent indices
        start = key_index[i]
        end = key_index[i+1]
      if i == len(key_index) - 1: # For the last key_index, search a number of subsequent paragraphs
        start = key_index[i]
        #end = key_index[i] + 30
        #end = key_index[i] + 70
        if key_index[i] + 100 < len(a):
          end = key_index[i] + 100
        else:
          end = len(a)

      for j in range(end-start+1):
        print(start,end,key_index[i])
        merge_result, start = merge(start,end,key_index[i],a) # Merge intermediate sentences by length, with max length capped at 3600
        #print(start,end,end-2)
        section_list.append(merge_result)
        if start == end - 1: # Stop once the last segment has also been merged
          break
        if start >= len(a) - 10: # Stop when approaching the end of the paper
          break

    new_list = [] # Deduplicate section_list
    for i in section_list:
      if i not in new_list:
        new_list.append(i)

    section_content = []
    for i in range(len(new_list)):
      text = ''
      for j in range(len(new_list[i])):
        text += a[new_list[i][j]]
      section_content.append(text)

    # Export GPT input for coreference extraction
    content_cor = {"text" : section_content} # Convert the list to a dictionary
    content_cor = DataFrame(content_cor) # Convert the dictionary to a DataFrame
    content_cor.to_csv('GPT_input_coreference'+(paper_id)+'.csv',index=False)

    # Export GPT input for reaction content extraction
    content_react = {"text" : section_content} # Convert the list to a dictionary
    content_react = DataFrame(content_react) # Convert the dictionary to a DataFrame
    content_react.to_csv('GPT_input_'+str(paper_id)+'.csv',index=False)


    # Send input to GPT for coreference extraction
    result_cor = []

    for i in tqdm(range(len(section_content))):
      completion = prompt_function_gpt4_1v1(section_content[i])
      #print(section_content[i])
      text_print = ""
      for chunk in completion:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
          text_print = text_print + chunk.choices[0].delta.content
      print(text_print)

      result_cor.append(text_print)
      time.sleep(10)

    # Export GPT output
    output_cor = {"text" : result_cor} # Convert the list to a dictionary
    output_cor = DataFrame(output_cor) # Convert the dictionary to a DataFrame
    success_list_cor.append(paper_id)
    output_cor.to_csv('GPT_output_coreference'+str(paper_id)+'.csv',index=False)

    # Send input to GPT
    result_react = []

    for i in tqdm(range(len(section_content))):
      completion = prompt_function_general_procedure(section_content[i])
      text_print = ""
      for chunk in completion:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
          text_print = text_print + chunk.choices[0].delta.content
      print(text_print)

      result_react.append(text_print)
      time.sleep(10)

    # Export GPT output
    output_react = {"text" : result_react} # Convert the list to a dictionary
    output_react = DataFrame(output_react) # Convert the dictionary to a DataFrame
    success_list_react.append(paper_id)
    output_react.to_csv('GPT_output_react'+str(paper_id)+'.csv',index=False)