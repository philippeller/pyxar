import copy

class Pixel(object):

    def __init__(self, col, row, trim = 15, mask = False):
        self._col = col
        self._row = row
        self.trim = trim
        self.mask = mask

    @property
    def col(self):
        return self._col

    @property
    def row(self):
        return self._row

    @property
    def trim(self):
        return self._trim

    @trim.setter
    def trim(self,value):
        if isinstance(value, bool):
            if value == False:
                self._trim = 15
            else:
                raise Exception("Trim Value must be integer in [0,15]")
        else:
            try:
                trim_value = int(value)
            except ValueError:
                raise Exception("Trim Value must be integer in [0,15]")
            assert trim_value < 16
            self._trim = trim_value
        return self._trim

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, value):
        self._mask = bool(value)
        return self._mask

    def __str__(self):
        return "Pixel %s, %s"%(self._col,self._row)

    def __repr__(self):
        return "Pixel %s, %s"%(self._col,self._row)


class DAC(object):
    
    def __init__(self,number, name, bits = 8, value=0):
        self._number = number
        self._name = name
        self._bits = bits
        self.value = value

    @property
    def number(self):
        return self._number

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,value):
        try:
            set_value = int(value)
        except ValueError:
            raise Exception("DAC Value must be integer in [0,%s]"%2**self._bits)
        assert set_value < 2**self._bits
        self._value = set_value
        return self._value

    def __str__(self):
        return "DAC %s: %s"%(self._name,self._value)

    def __repr__(self):
        return "DAC %s: %s"%(self._number,self._value)
    

class Roc(object):

    def __init__(self, config,number=0):
        """Initialize ROC (readout chip)."""
        self._n_rows = int(config.get('ROC','rows'))
        self._n_cols = int(config.get('ROC','cols'))
        self._n_pixels = self._n_rows*self._n_cols
        self.number = number

        #define pixel array
        self._pixel_array = []
        # fill pixel array
        for col in range(self._n_cols):
            self._pixel_array.append(copy.copy([]))
            for row in range(self._n_rows):
                self._pixel_array[col].append(Pixel(col, row))

        #define dac list
        self._dac_list = []
        self._dac_number_to_name = eval(config.get('ROC','dac_dict'))
        self._dac_name_to_number = {v:k for k, v in self._dac_number_to_name.items()}
        self._dac_dict = {}
        dac_bits = eval(config.get('ROC','dac_bits'))
        for dac_number in self._dac_number_to_name:
            self._dac_dict[dac_number] = (DAC(dac_number,self._dac_number_to_name[dac_number],dac_bits[dac_number]))

    @property
    def n_rows(self):
        """Get number of rows."""
        return self._n_rows

    @property
    def n_cols(self):
        """Get number of columns."""
        return self._n_cols
    
    @property
    def n_pixels(self):
        """Get number of pixels."""
        return self._n_pixels

    #get pixel object
    def pixel(self,col,row):
        return self._pixel_array[col][row]

    # get dac object
    def dac(self,dac_id):
        if isinstance(dac_id,str):
            return self._dac_dict[self._dac_name_to_number[dac_id]]
        elif isinstance(dac_id,int):
            return self._dac_dict[dac_id]

    #iterator over all pixels
    def pixels(self):
        col = 0
        while col < self._n_cols:
            row = 0
            while row < self._n_rows:
                yield self._pixel_array[col][row]
                row += 1
            col += 1

    #iterator over column
    def col(self,col):
        row = 0
        while row < self._n_rows:
            yield self._pixel_array[col][row]
            row += 1

    #iterator over row
    def row(self,row):
        col = 0
        while col < self._n_cols:
            yield self._pixel_array[col][row]
            col += 1

    #return true if any pixel is masked
    @property
    def mask(self):
        return any([pix.mask for pix in self.pixels()])

    #set all pixel masks of chip
    @mask.setter
    def mask(self,value):
        for pix in self.pixels():
            pix.mask = value

    def __repr__(self):
        return "ROC %s"%self.number

    def __str__(self):
        return "ROC %s"%self.number

class TBM(object):
    def __init__(self,config,number=0):
        self._n_channels = int(config.get('TBM','channels'))
        self.number = number

    def __repr__(self):
        return "TBM %s"%self.number

    def __str__(self):
        return "TBM %s"%self.number

class Module(object):
    def __init__(self, config):
        """Initialize Module"""
        self._n_rocs = int(config.get('Module','rocs'))
        self._n_tbms = int(config.get('Module','tbms'))

        #define collections
        self._roc_list = []
        self._tbm_list = []
        # fill collections
        for roc in range(self._n_rocs):
            self._roc_list.append(Roc(config,roc))
        for tbm in range(self._n_tbms):
            self._tbm_list.append(TBM(config,tbm))

    @property
    def n_rocs(self):
        return self._n_rocs

    @property
    def n_tbms(self):
        return self._n_tbms

    #get roc object
    def roc(self,roc):
        return self._roc_list[roc]

    #iterator over rocs
    def rocs(self):
        roc = 0
        while roc < self._n_rocs:
            yield self.roc(roc)
            roc += 1

    #get pixel object
    def pixel(self,roc,col,row):
        return self.roc(roc).pixel(col,row)

    #get dac object
    def dac(self,roc,dac_id):
        return self.roc(roc).dac(dac_id)


if __name__=='__main__':
    from BetterConfigParser import BetterConfigParser
    config = BetterConfigParser()
    config.read('../data/module')
    
    #make a module from config
    m = Module(config)

    #access a single pixel
    print m.roc(5).pixel(12,13)
    #or
    print m.pixel(5,12,13)

    #iterate
    for roc in m.rocs():
        roc.dac('Vana').value = 155
        print roc, roc.dac('Vana')

    #set individual DAC, by name or number
    m.roc(1).dac('Vana').value = 0
    print m.roc(1).dac('Vana')
    m.roc(1).dac(2).value = 0
    print m.roc(1).dac('Vana')

    #mask a single pixel
    m.pixel(2,45,6).mask = True
    print m.roc(2).mask
    #unmask all pixels of roc 2
    m.roc(2).mask = False
    print m.roc(2).mask