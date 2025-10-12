from novelai_api.GlobalSettings import GlobalSettings
from novelai_api.Preset import Model, Preset
from novelai_api.Tokenizer import Tokenizer
from novelai_api.utils import b64_to_tokens
from xoxxox.naiapi.boilerplate import API
from xoxxox.shared import Custom, LibLog

#---------------------------------------------------------------------------

class TttPrc:
  def __init__(self, config="xoxxox/config_tttnai_000", **dicprm):
    diccnf = Custom.update(config, dicprm)
    self.nmodel = getattr(Model, diccnf["nmodel"]) # Erato, Kayra
    if diccnf["nmodel"] == "Erato":
      self.nbytes = 4
    else:
      self.nbytes = 2
    self.preset = Preset.from_official(self.nmodel, diccnf["preset"]) # Erato (小説家), Kayra (Carefree)
    self.preset.min_length =  4
    self.preset.max_length = 20
    self.config = GlobalSettings()
    self.conlog = {}

  def status(self, config="xoxxox/config_tttnai_000", **dicprm):
    diccnf = Custom.update(config, dicprm)
    self.expert = diccnf["expert"]
    if not (self.expert in self.conlog):
      self.conlog[self.expert] = LibLog.getlog(diccnf["conlog"]) # LOG
      self.conlog[self.expert].catsys(diccnf) # LOG

  async def infere(self, txtreq):
    async with API() as hdlapi:
      apinai = hdlapi.api
      prompt = self.conlog[self.expert].catreq(txtreq) # LOG
      print("prompt[", prompt, "]", sep="", flush=True) # DBG
      tknprm = Tokenizer.encode(self.nmodel, prompt)
      rawifr = await apinai.high_level.generate(
        tknprm,
        self.nmodel,
        self.preset,
        self.config
      )
      #print("rawifr[", rawifr, "]", sep="", flush=True) # DBG
      txtifr = Tokenizer.decode(self.nmodel, b64_to_tokens(rawifr["output"], self.nbytes))
      print("txtifr[" + txtifr + "]", flush=True) # DBG
      txtres, txtopt = self.conlog[self.expert].arrres(txtifr) # LOG
      print("txtres[" + txtres + "]", flush=True) # DBG
      print("txtopt[" + txtopt + "]", flush=True) # DBG
      self.conlog[self.expert].catres(txtres) # LOG
      return (txtres, txtopt)
