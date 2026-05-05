=== /plan #1 standalone-violation-analyzer ===
so here's my grand idea. analyze_violations.py from certora-dashboard aka ~/certora/localdashboard can be moved to ~/certora/violationanalyzer-release which will stop being a 'woohoo all          
submodules here' and instead use the standard pytoml approach we used so far. it would depend on preaudit because of traceextractor of course, thus also on autosetup. it would use for ci the     
setup-dependencies approach used here. then, once that's introduced (in a side branch since people use violationanalyzer right now!), we sort out rag db, by taking from                            
~/certora/aicomposerragdbpublish. then, we introduce ci tests for the violation analyzer.         


SG: FIRST LET'S GET RID OF THAT TRACE EXTRACTOR DEPENDENCY

- get_default_rag_db should move from preaudit to violation analyzer. was originally in autosetup