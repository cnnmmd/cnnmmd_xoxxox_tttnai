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
    self.nmodel = getattr(Model, diccnf["nmodel"]) # Erato, Kayra
    if diccnf["nmodel"] == "Erato":
      self.nbytes = 4
    else:
      self.nbytes = 2
    self.preset = Preset.from_official(self.nmodel, diccnf["preset"]) # Erato (小説家), Kayra (Carefree)
    self.preset.min_length =  4
    self.preset.max_length = 20
    self.config = GlobalSettings()

  def status(self, config="xoxxox/config_tttnai_000", **dicprm):
    diccnf = Custom.update(config, dicprm)
    # 設定：全般
    self.lsthed = []
    self.lstbdy = []
    self.frmsys = "{elmsys}\n"
    self.frmusr = "{txtsrc}{txtdef}{elmusr}\n"
    self.frmagt = "{txtdst}{txtdef}{elmagt}\n"
    # 設定：個別
    self.maxbdy = diccnf["prmmax"]
    self.nulagt = diccnf["nuloth"]
    self.dictlk = {
      "elmsys": diccnf["status"],
      "txtsrc": diccnf["rolslf"],
      "txtdst": diccnf["roloth"],
      "elmusr": diccnf["inislf"],
      "elmagt": diccnf["inioth"],
      "txtdef": "＞",
    }
    self.lsthed.append(self.frmsys.format_map(self.dictlk))
    self.lstbdy.append(self.frmusr.format_map(self.dictlk))
    self.lstbdy.append(self.frmagt.format_map(self.dictlk))

  async def infere(self, txtreq):
    async with API() as hdlapi:
      apinai = hdlapi.api
      # 生成：導入
      self.dictlk["elmusr"] = txtreq
      self.lstbdy.append(self.frmusr.format_map(self.dictlk))
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
        elmagt = re.findall(self.dictlk["txtdst"] + self.dictlk["txtdef"] + "(.*)", infdec)[0]
      except Exception as e:
        elmagt = ""
      if elmagt == "":
        elmagt = self.nulagt
      # ログ：追加
      self.dictlk["elmagt"] = elmagt
      self.lstbdy.append(self.frmagt.format_map(self.dictlk))
      if len(self.lstbdy) > self.maxbdy * 2:
        self.lstbdy.pop(0)
        self.lstbdy.pop(0)
      # 結果：返却
      txtres = elmagt
      return txtres
