from discord import Embed, Colour


async def account_layer_selection_message(destination, layer: int):
    wallet_selection_info = Embed(title=":interrobang: Account Layer Selection Error :interrobang: ",
                                  color=Colour.red())
    wallet_selection_info.add_field(name=f':warning: Wrong Layer Selection :warning:',
                                    value=f'You have selected wallet layer number {layer}. Only two available options'
                                          f' are :arrow_double_down:  ',
                                    inline=False)
    wallet_selection_info.add_field(name=f':one: Layer Custodial User Wallet by Memo',
                                    value=f'By selecting layer 1, you will be making transaction to users wallet '
                                          f'which is identified in the system by unique MEMO given for the user uppon'
                                          f' registration with the Crypto Link System.',
                                    inline=False)
    wallet_selection_info.add_field(name=f':two: Layer Custodial User Wallet by Public Address',
                                    value=f'By selecting layer 2, transaction will be done to users personal hot wallet '
                                          f'managed by the Crypto Link System which was created throughout the process'
                                          f' of registering custodial wallet.',
                                    inline=False)
    await destination.send(embed=wallet_selection_info)
