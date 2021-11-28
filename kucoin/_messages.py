"""Print messages."""
def ledger(verbose,name,di,de):
    if verbose:
        print("extracting %s ledger...%s thru %s" %(
            name,
            di.strftime("%Y-%m-%d"),
            de.strftime("%Y-%m-%d"),
            ))
            
def usd_fills(verbose,name,di,de):
    if verbose:
        print("extracting %s USD fills...%s thru %s" %(
            name,
            di.strftime("%Y-%m-%d"),
            de.strftime("%Y-%m-%d"),
            ))
