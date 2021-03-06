"""Usage:
ccf.exe <data_folder> [options]
ccf.exe create <output_folder>

Options:
  -h --help
"""
import sys
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from core.error_handling import permission_popup
import core.logfuncs as lf
import core.filefuncs as ff


@lf.log_output
def get_trendline(pps_df):

    y = pps_df['photometer'].values
    x = pps_df['camera'].values

    def squared_percentage_error(w):
        slope, intercept = w
        y_pred = slope*x + intercept
        spe = ((y_pred - y)/y)**2
        return spe.sum()

    slope, intercept = minimize(squared_percentage_error, [1.0, 0.0]).x
    trendline = np.array([slope, intercept])
    return trendline

@lf.log_output
def get_final_trendline(trendlines, w_outputs):
    weighted_trendlines = {color: trendline*w_outputs[color] for color, trendline in trendlines.items()}
    final_trendline = np.array(list(weighted_trendlines.values())).sum(axis=0)
    return final_trendline

@permission_popup
def main():
    logger, docopt_args, data_folder = lf.start_script(__doc__, 'ccf.log')
    paths = ff.get_paths(data_folder)
    
    if docopt_args['create']:
        path = docopt_args['<output_folder>']
        src = Path(sys.path[0]).joinpath('ccf-input-template.csv')
        dst = Path(path).joinpath('ccf-input.csv')
        if dst.exists():
            print(f'{dst} already exists')
        else:
            shutil.copy(src, dst)
    else:
        drop_cols = ['photometer', 'camera']
        input_df = pd.read_csv(paths['ccf_input']).replace(0, np.NaN).dropna()
        # input_df = pd.read_csv(docopt_args['<input_path>']).dropna(subset=drop_cols, how='all')
        final_trendlines = {}
        for pps in input_df['pps'].unique():
            logger.info(f'\nPPS: {pps}')
            pps_df = input_df.query('pps==@pps')
            final_trendlines[pps] = get_trendline(pps_df)
            
        # output_path =
        # if docopt_args['-o'] is not None:
        #     output_path = Path(docopt_args['-o']).joinpath(output_path)
        output_df = pd.DataFrame(data=final_trendlines, index=['slope', 'intercept']).T
        output_df.to_csv(Path(data_folder).joinpath('ccf-output.csv'))
        output_df.to_csv(Path(ff.APPDATA_DIR).joinpath('ccf-output.csv'))
        
        input_df.to_csv(Path(data_folder).joinpath('ccf-input.csv'), index=False)
        input_df.to_csv(Path(ff.APPDATA_DIR).joinpath('ccf-input.csv'), index=False)



if __name__ == '__main__':
    main()
