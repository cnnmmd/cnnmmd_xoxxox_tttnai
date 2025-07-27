import re
from novelai_api.GlobalSettings import GlobalSettings
from novelai_api.Preset import Model, Preset
from novelai_api.Tokenizer import Tokenizer
from novelai_api.utils import b64_to_tokens
from xoxxox.naiapi.boilerplate import API
from xoxxox.shared import Custom

#---------------------------------------------------------------------------

class TttPrc:
  def __init__(self, config="xoxxox/config_tttnai_000", **dicprm):
    diccnf = Custom.update(config, dicprm)
    self.nmodel = eval(diccnf["nmodel"]) # Model.Erato, Model.Kayra
    if diccnf["nmodel"] == "Model.Erato":
      self.nbytes = 4
    else:
      self.nbytes = 2
    self.smodel = diccnf["nmodel"]
    self.preset = Preset.from_official(self.nmodel, diccnf["preset"]) # Erato (小説家), Kayra (Carefree)
    self.preset.min_length =  4
    self.preset.max_length = 20
    self.config = GlobalSettings()

  def status(self, config="xoxxox/config_tttnai_000", **dicprm):
    diccnf = Custom.update(config, dicprm)
    # 設定：全般
    self.lsthed = []
    self.lstbdy = []
    self.txtdef = "＞"
    self.frmsys = "f\"{elmsys}\\n\""
    self.frmusr = "f\"{self.txtsrc + self.txtdef + elmusr}\\n\""
    self.frmagt = "f\"{self.txtdst + self.txtdef + elmagt}\\n\""
    # 設定：個別
    self.maxbdy = diccnf["prmmax"]
    self.txtsrc = diccnf["rolslf"]
    self.txtdst = diccnf["roloth"]
    self.nuloth = diccnf["nuloth"]
    elmsys = diccnf["status"]
    self.lsthed.append(eval(self.frmsys))
    elmusr = diccnf["inislf"]
    self.lstbdy.append(eval(self.frmusr))
    elmagt = diccnf["inioth"]
    self.lstbdy.append(eval(self.frmagt))

  async def infere(self, txtreq):
    async with API() as hdlapi:
      apinai = hdlapi.api
      # 生成：導入
      elmusr = txtreq
      self.lstbdy.append(eval(self.frmusr))
      strlog = "".join(self.lsthed + self.lstbdy)
      #print("strlog[" + strlog + "]") # DBG
      # 生成：推定
      prompt = Tokenizer.encode(self.nmodel, strlog)
      infenc = await apinai.high_level.generate(
        prompt,
        self.nmodel,
        self.preset,
        self.config
      )
      infdec = Tokenizer.decode(self.nmodel, b64_to_tokens(infenc["output"], self.nbytes))
      #print("infdec[" + infdec + "]") # DBG
      # 結果：加工
      try:
        elmagt = re.findall(self.txtdst + self.txtdef + "(.*)", infdec)[0]
      except Exception as e:
        elmagt = ""
      if elmagt == "":
        elmagt = self.nuloth
      # ログ：追加
      self.lstbdy.append(eval(self.frmagt))
      if len(self.lstbdy) > self.maxbdy * 2:
        self.lstbdy.pop(0)
        self.lstbdy.pop(0)
      # 結果：返却
      txtres = elmagt
      return txtres
