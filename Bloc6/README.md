# Project Jedha : Early-prediction-alzheimer

## Problem description:
The project is focused on building innovative models for early detection of AD/ADRD using audio data.
Current methods of screening for AD/ADRD are time intensive and difficult to perform. Models that can flag individuals with a high likelihood of cognitive decline early based on vocal characteristics have the potential to catch and treat cognitive decline earlier, and to reduce disparities in care for marginalized groups. Speech data would be a highly cost-effective and noninvasive method for assessing cognitive decline.

## Data:
The feature data in this competition is a series of audio recordings collected from individuals diagnosed with some form of cognitive decline as well as healthy controls.
The data include 2,058 individuals from multiple different studies. Participants have access to ~30-second clips from the raw audio recordings, as well as pre-generated acoustic features. Participants can choose whether to use the audio recordings, the pre-generated features, or both. The focus of this challenge is on acoustic biomarkers, or voice-based features that may signal the presence of cognitive impairment. However, we encourage solvers to explore all possible features, including linguistic and semantic ones.

## Metadata:
metadata.csv provides basic information about each individual in the dataset, and includes both the train and test split. metadata.csv includes the following columns:
- uid (str): A unique identifier for the individual. Each row is a unique individual.
- age (int): Patient age.
- gender (str): Patient gender. In this dataset, only the categories "male" and "female" are included.
- split (str): Dataset split, either "train" or "test". There are 1,646 individuals in the train set, and 412 in the test set.
- hash (str): Hash of the audio .mp3 file for the individual. This can be useful to verify the integrity of your own downloaded file. Hashes are generated using the MD5 hash function. In python, the MD5 hash of a file can be generated with hashlib.md5(file_path.read_bytes()).hexdigest() using the hashlib library. Note that file_path must be a pathlike object (eg. pathlib.Path), not a string.
- filesize_kb (float): Size of the audio .mp3 file for the individual in KB.

## Audio files:
Raw audio .mp3 files are available for all individuals in both the train and the test set. Each audio recording corresponds to a different individual. Recordings have been diarized and spliced together to minimize interruptions from other speakers. Each recording is 30 seconds or less.

## Pre-generated acoustic features:
Along with raw audio files, we have a set of pre-generated acoustic features. 
Each row in train_features.csv represents a distinct 0.2-second slice of a recording, and is a unique combination of uid and segment_start_sec.

train_features.csv and test_features.csv each include the following columns:
- uid (str): A unique identifier for the individual.
- segment_start_sec, segment_end_sec (float): The start and end time within the patient's full audio recording in seconds.
- F0semitoneFrom27.5Hz_sma3nz_amean to equivalentSoundLevel_dBp (float): 88 different pre-generated acoustic features, extracted from each segment using the eGeMAPS V02 parameter set. These features include pitch, formants, speech rate, and other key acoustic markers that may be indicative of cognitive decline. Features were generated using the opensmile package. Multiple studies have used this set of acoustic parameters to study detection of Alzheimer's Disease (J. Chen, J. Ye, F. Tang, and J. Zhou, 2021; F. Haider, S. de la Fuente, and S. Luz, 2020).

## Labels:
The target variable is the cognitive status of each individual. There are three possible diagnoses:
1. Control: Healthy individual, aging in a typical way
2. MCI: Mild cognitive impairment (MCI). While not everyone who has MCI develops dementia, MCI is a useful indicator of risk that supports early detection of AD/ADRD.
3. ADRD: An advanced diagnosis. This includes primary progressive aphasia (PPA), probable AD, and AD. Note that primary progressive aphasia (PPA) is distinct from Alzheimer's. They are grouped in this competition because both represent a form of advanced decline, and they share many symptoms and neurodegenerative conditions

train_labels.csv includes the following columns:
- uid (str): Unique identifier for the individual. Each row is one individual.
- diagnosis_control (float, 0.0 or 1.0): Whether the individual is a healthy control.
- diagnosis_mci (float, 0.0 or 1.0): Whether the individual was diagnosed with mild cognitive impairment.
- diagnosis_adrd (float, 0.0 or 1.0): Whether the individual was diagnosed with advanced decline (primary progressive aphasia, probable AD, or AD).

In each row, only one of diagnosis_control, diagnosis_mci, or diagnosis_adrd will be equal to 1.  
