def namedlist(class_name,var_names):
    def __init__(self,*args,**kwargs):
        valid_args = var_names.split()
        for arg in args:
            arg_name = valid_args.pop(0)
            setattr(self,arg_name,arg)
        for k,v in kwargs.items():
            if k not in valid_args:
                raise Exception
            arg_name = valid_args.pop(valid_args.index(k))
            setattr(self,arg_name,v)
        if len(valid_args)>0:
            raise Exception("Missing arguments")
            
    def __str__(self):
        argslist = ', '.join(["{}={}".format(vn,getattr(self,vn)) for vn in var_names.split()])
        return "{}({})".format(class_name,argslist)
    
    def __repr__(self):
        return self.__str__()
    
    cls = type(class_name,(),{"__init__":__init__,"__str__":__str__,"__repr__":__repr__})
    return cls

Bid = namedlist('Bid','account_id volume price provision')
Ask = namedlist('Ask','account_id volume price provision')

class KwargsException(Exception):
    def __init__(self,*args,**kwargs):
        super(KwargsException,self).__init__(*args)
        for k,v in kwargs.iteritems():
            setattr(self,k,v)

class BankruptException(KwargsException):
    pass

class InsufficientFundsException(KwargsException):
    pass

class NotEnoughAssetException(KwargsException):
    pass

class InactiveAccountException(KwargsException):
    pass

class Account(object):
    
    def __init__(self, name, id, init_balance):
        self.name = name
        self.id = id
        self._balance = init_balance
        self._assets = {}
        self._active = True
        
    @property
    def balance(self):
        return self._balance
    
    @property
    def assets(self):
        return {k:v for k,v in self._assets.items()}
        
    def credit(self, amount):
        if not self._active:
            raise InactiveAccountException
        self._balance += amount
        return True
        
    def debit(self, amount, force=False):
        if not self._active:
            raise InactiveAccountException
        if amount > self._balance and force:
            paid = self._balance
            left = amount - self._balance
            self._balance = 0
            raise BankruptException(paid=paid, left=left)
        elif amount > self._balance:
            raise BankruptException
        self._balance -= amount
        return True
    
    def take_asset(self, asset, quantity, force=False):
        if not self._active:
            raise InactiveAccountException
        if quantity > self._assets.get(asset,0) and force:
            taken = self._assets[asset]
            left = quantity - _assets[asset]
            self._assets[asset] = 0
            raise NotEnoughAssetException(asset=asset, taken=taken, left=left)
        elif quantity > self._assets.get(asset,0):
            raise NotEnoughAssetException(asset=asset)
        self._assets[asset] -= quantity
        return True
        
    def put_asset(self, asset, quantity):
        if not self._active:
            raise InactiveAccountException
        self._assets.setdefault(asset,0)
        self._assets[asset] += quantity
        return True
    
    def has_asset(self, asset, quantity):
        return self._assets.get(asset,0)>=quantity
    
    def has_credit(self, amount):
        return self._balance>=amount
    
    def close(self):
        if not self._active:
            raise InactiveAccountException
        self._active = False
        amount = self._balance
        assets = self.assets
        self._balance = 0
        self._assets = {}
        return amount, assets
    
    def deactivate(self):
        self._active = False
    
class Exchange(object):
    
    def __init__(self, assets):
        self._assets = assets
        self._orders = {asset:{'bid':[],'ask':[]} for asset in assets}
        self._accounts = {}
        
    def open_account(self, name, init_balance):
        assert init_balance >= 0, "Negative Balance"
        id = max(self._accounts.keys()+[0]) + 1
        account = Account(name, id, init_balance)
        self._accounts[id] = account
        return id
    
    def close_account(self, account_id):
        assert account_id in self._accounts, "Account ID not found"
        account = self._accounts[account_id]
        for asset in self._assets:
            for bid in self._orders[asset]['bid']:
                if bid.account_id == account_id:
                    provision = bid.provision
                    bid.volume = 0
                    bid.provision = 0
                    account.credit(provision)
            for bid in self._orders[asset]['ask']:
                if bid.account_id == account_id:
                    volume = bid.volume
                    bid.volume = 0
                    bid.provision = 0
                    account.put_asset(asset,volume)
        amount, assets = account.close()
        return amount, assets
    
    def credit_account(self, account_id, amount):
        assert account_id in self._accounts, "Account ID not found"
        assert amount>0, "Negative or null amount"
        account = self._accounts[account_id]
        return account.credit(amount)
        
    def add_asset(self, account_id, asset, quantity):
        assert asset in self._assets, "Asset does not exist"
        assert account_id in self._accounts, "Account ID not found"
        assert quantity>0, "Negative or null quantity"
        account = self._accounts[account_id]
        return account.put_asset(asset, quantity)
    
    def get_balance(self, account_id):
        assert account_id in self._accounts, "Account ID not found"
        account = self._accounts[account_id]
        return account.balance
    
    def get_assets(self, account_id):
        assert account_id in self._accounts, "Account ID not found"
        account = self._accounts[account_id]
        return account.assets
    
    def post_order(self, account_id, asset, side, price, volume):
        assert asset in self._assets, "Asset does not exist"
        assert side in ('bid','ask'), "Side must be either bid or ask"
        assert account_id in self._accounts, "Account ID not found"
        account = self._accounts[account_id]
        amount = volume*price
        if side == 'bid':
            try:
                account.debit(amount)
            except BankruptException:
                return False
            self._orders[asset][side].append(Bid(account_id,volume,price,amount))
            return True
        elif side =='ask':
            try:
                account.take_asset(asset,volume)
            except NotEnoughAssetException:
                return False
            self._orders[asset][side].append(Ask(account_id,volume,price,volume))
            return True
            
    def take_order(self,account_id, asset, side, price, volume):
        assert asset in self._assets, "Asset does not exist"
        assert side in ('bid','ask'), "Side must be either bid or ask"
        assert account_id in self._accounts, "Account ID not found"
        orders = [order for order in self._orders[asset][side] if order.price==price]
        assert sum([o.volume for o in orders])>=volume, "Insufficient volume on the market at this price"
        
        account = self._accounts[account_id]
        amount = volume*price
        
        if side == 'bid':
            assert account.has_asset(asset, volume), "Insufficient volume on the account"
            try:
                account.take_asset(asset,volume)
            except NotEnoughAssetException:
                return False
            volume_left = volume
            while volume_left > 0:
                order = orders.pop(0)
                counterparty = self._accounts[order.account_id]
                volume_available = order.volume
                if volume_left > volume_available:
                    account.credit(volume_available*order.price)
                    counterparty.put_asset(asset, volume_available)
                    order.volume = 0
                    order.provision = 0
                    volume_left -= volume_available
                else:
                    account.credit(volume_left*order.price)
                    counterparty.put_asset(asset,volume_left)
                    order.volume -= volume_left
                    order.provision -= volume_left*order.price
                    volume_left = 0
                    
            return True
        
        elif side =='ask':
            assert account.has_credit(amount), "Insufficient credit on the account"
            try:
                account.debit(amount)
            except InsufficientFundsException:
                return False
            volume_left = volume
            while amount_left > 0:
                order = orders.pop(0)
                counterparty = self._accounts[order.account_id]
                volume_available = order.volume
                if volume_left > volume_available:
                    account.put_asset(asset, volume_available)
                    counterparty.credit(volume_available*order.price)
                    order.volume = 0
                    order.provision = 0
                    volume_left -= volume_available
                else:
                    account.put_asset(asset, volume_left)
                    counterparty.credit(volume_left*order.price)
                    order.volume -= volume_left
                    order.provision -= volume_left
                    volume_left = 0
            return True
        
    def get_book(self, asset):
        assert asset in self._assets, "Asset does not exist"
        bids = {}
        
        for order in self._orders[asset]['bid']:
            if order.volume == 0:
                continue
            bids.setdefault(order.price,0)
            bids[order.price] += order.volume
        asks = {}
        
        for order in self._orders[asset]['ask']:
            if order.volume == 0:
                continue
            asks.setdefault(order.price,0)
            asks[order.price] += order.volume
        
        return {'bid':bids, 'ask':asks}
        