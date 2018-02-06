import sys
import peerscout.docvec_model

# provide backwards compatibility for old pickle models
sys.modules[__name__] = peerscout.docvec_model
