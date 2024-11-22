import argparse
import json
from pathlib import Path
from src.core.data_processor import DataProcessor

def main():
    parser = argparse.ArgumentParser(description='Process text data with ThunderData')
    
    parser.add_argument('input_file', 
                       help='Path to input file (supported: csv, txt, json, xlsx)')
    
    parser.add_argument('--config', required=True,
                       help='Path to JSON configuration file for transformations')
    
    parser.add_argument('--output', required=True,
                       help='Path to save processed data')
    
    parser.add_argument('--output-format', choices=['csv', 'json', 'xlsx'],
                       default='csv', help='Output file format (default: csv)')
    
    # Optional arguments for data loading
    parser.add_argument('--encoding', default='utf-8',
                       help='File encoding (default: utf-8)')
    
    parser.add_argument('--sheet-name', default=0,
                       help='Sheet name/index for Excel files (default: 0)')
    
    args = parser.parse_args()
    
    # Load transformation configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        return
    
    # Initialize processor
    processor = DataProcessor()
    
    try:
        # Load data
        print(f"Loading data from {args.input_file}...")
        kwargs = {'encoding': args.encoding}
        if Path(args.input_file).suffix == '.xlsx':
            kwargs['sheet_name'] = args.sheet_name
        
        processor.load_data(args.input_file, **kwargs)
        
        # Configure and apply transformations
        print("Configuring transformations...")
        processor.configure_transformations(config)
        
        print("Processing data...")
        result = processor.process_data()
        
        # Save results
        print(f"Saving results to {args.output}...")
        processor.save_results(args.output, format=args.output_format)
        
        print("Processing completed successfully!")
        
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == '__main__':
    main()
