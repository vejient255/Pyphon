import traceback
try:
    import main
    main.run_test()
except Exception as e:
    print('ERROR IN APP:')
    traceback.print_exc()
