#!/usr/bin/env python3
"""Test script for musician API functionality"""

from csv_data_processor import CSVDataProcessor

def test_musician_functionality():
    processor = CSVDataProcessor()
    
    # Test get_musicians_for_dropdown
    musicians = processor.get_musicians_for_dropdown()
    print(f'Musicians: {len(musicians)}')
    print(f'First few musicians: {musicians[:5]}')
    print()
    
    # Test get_musician_songs
    musician_songs = processor.get_musician_songs('BRUWAR')
    print(f'BRUWAR songs: {len(musician_songs)}')
    if musician_songs:
        print(f'First song: {musician_songs[0]}')
    print()
    
    # Test get_musician_by_id
    musician_details = processor.get_musician_by_id('BRUWAR')
    if musician_details:
        print(f'BRUWAR details: {musician_details["name"]}')
        print(f'Total songs: {len(musician_details["songs"])}')

if __name__ == "__main__":
    test_musician_functionality()