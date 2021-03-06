"""Usage:
main_sequence.exe  <data_folder> <default_pps> <brightest_pps> [options]

Arguments:
  data_folder       directory where data for this test sequence will be stored
  default_pps       name of default preset picture setting
  brightest_pps     name of brightest preset picture setting

Options:
  -h --help
  --defabc      include abc on tests for default pps
  --hdr=pps     specify hdr preset picture setting for testing
  --hdrabc      include abc on tests for hdr pps
  --brabc       include abc on tests for brightest pps
  --qs          tv has quickstart feature
  --qsoff=secs  tv has quickstart off by default, number of seconds to wake with quickstart off
"""
import sys
from pathlib import Path
import core.sequence.sequence as ts
import core.sequence.command_sequence as cs
import core.report.report_data as rd
import core.logfuncs as lf


def get_test_order(docopt_args, ccf_pps_list):
    """Determine test order from option arguments."""
    test_order = ts.setup_tests(ccf_pps_list)
    
    test_order += ['default', 'brightest']
    if docopt_args['--hdr']:
        test_order += ['hdr10']
    if not docopt_args['--defabc']:
        test_order += ['default_low_backlight']
    if not docopt_args['--brabc']:
        test_order += ['brightest_low_backlight']
    if docopt_args['--hdr'] and not docopt_args['--hdrabc']:
        test_order += ['hdr10_low_backlight']
        
    for lux_level in [100, 35, 12, 3]:
        if docopt_args['--defabc']:
            test_order += [f'default_{lux_level}']
        if docopt_args['--brabc']:
            test_order += [f'brightest_{lux_level}']
        if docopt_args['--hdr'] and docopt_args['--hdrabc']:
            test_order += [f'hdr10_{lux_level}']
    
    test_order += [
        # 'standby_passive',
        # 'passive_waketime',
        'standby_active_low',
        'active_low_waketime',
        # 'standby_multicast',
        # 'multicast_waketime',
        # 'standby_echo',
        # 'echo_waketime',
        # 'standby_google',
        # 'google_waketime',
    ]
    return test_order


def get_simple_test_order(docopt_args):
    """Determine test order from option arguments."""
    test_order = ['screen_config', 'stabilization', 'manual_ccf_default', 'manual_ccf_brightest']
    if docopt_args['--hdr']:
        test_order += ['manual_ccf_hdr']
    
    test_order += ['lum_profile']
    
    abc_def_tests = {
        True: ['default', 'default_100', 'default_35', 'default_12', 'default_3'],
        False: ['default', 'default_low_backlight']
    }
    test_order += abc_def_tests[bool(docopt_args['--defabc'])]
    
    abc_br_tests = {
        True: ['brightest', 'brightest_100', 'brightest_35', 'brightest_12', 'brightest_3'],
        False: ['brightest', 'brightest_low_backlight']
    }
    test_order += abc_br_tests[bool(docopt_args['--brabc'])]
    
    if docopt_args['--hdr']:
        abc_hdr_tests = {
            True: ['hdr10', 'hdr10_100', 'hdr10_35', 'hdr10_12', 'hdr10_3'],
            False: ['hdr10', 'hdr10_low_backlight']
        }
        test_order += abc_hdr_tests[bool(docopt_args['--hdrabc'])]
    return test_order


def main():
    logger, docopt_args, data_folder = lf.start_script(__doc__, 'main-sequence.log')
    
    # ccf_pps_list = ['default', 'brightest']
    # if docopt_args['--hdr']:
    #     ccf_pps_list += ['hdr10_default']
    ccf_pps_list = ['default']
        
    if Path(sys.path[0]).joinpath('simple.txt').exists():
        test_order = get_simple_test_order(docopt_args)
    else:
        test_order = get_test_order(docopt_args, ccf_pps_list)

    logger.info(test_order)
    
    rename_pps = {
        'default': docopt_args['<default_pps>'],
        'brightest': docopt_args['<brightest_pps>'],
        'hdr10_default': docopt_args['--hdr'],
        'abc_default': docopt_args['<default_pps>']
    }
    qs = docopt_args['--qs']
    qson = qs and (not docopt_args['--qsoff'] or float(docopt_args['--qsoff']) >= 10)
    test_seq_df = ts.create_test_seq_df(test_order, rename_pps, qs, qson)
    logger.info('\n' + test_seq_df.to_string())
    command_df = cs.create_command_df(test_seq_df)
    ts.save_sequences(test_seq_df, command_df, data_folder)
    rd.get_status_df(test_seq_df, None, {}, data_folder)


if __name__ == '__main__':
    main()
