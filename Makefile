include $(TOPDIR)/rules.mk

PKG_NAME:=wrtgram

PKG_VERSION:=3.0
PKG_RELEASE:=1

PKG_LICENSE:=GPL-2.0

include $(INCLUDE_DIR)/package.mk

define Package/wrtgram
  SECTION:=net
  CATEGORY:=Network
  TITLE:=Telegram BOT for openwrt
  URL:=https://github.com/nhAsif/WrtGram
  PKGARCH:=all
endef

define Package/wrtgram/description
  Telegram for use in openwrt. Its a BOT
  that executes selected commands in your router.
  Version: $(PKG_VERSION)-$(PKG_RELEASE)
  Info   : https://github.com/nhAsif/WrtGram
endef

define Package/wrtgram/conffiles
/etc/config/wrtgram
endef

define Build/Configure
endef

define Build/Compile
	find . -type f -print0 | xargs -0 sed -i 's/\r//g'
endef

define Package/wrtgram/install
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./etc/init.d/telegram_bot \
			./etc/init.d/lanports \
			./etc/init.d/hosts_scan \
		$(1)/etc/init.d

	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_CONF) ./etc/config/wrtgram \
		$(1)/etc/config/wrtgram
	
	$(INSTALL_DIR) $(1)/etc/wrtgram
	$(INSTALL_CONF) ./etc/wrtgram/macaddr.ignore \
		$(1)/etc/wrtgram/macaddr.ignore

	$(INSTALL_DIR) $(1)/usr/share/wrtgram
	echo "$(PKG_VERSION)-$(PKG_RELEASE)" > $(1)/usr/share/wrtgram/version
	
	$(INSTALL_DIR) $(1)/usr/lib/wrtgram
	$(INSTALL_BIN) ./usr/lib/wrtgram/wrtgramlib.py \
		$(1)/usr/lib/wrtgram

	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins/actions
	$(INSTALL_BIN) ./usr/lib/wrtgram/plugins/actions/* $(1)/usr/lib/wrtgram/plugins/actions/
	
	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins/help
	$(INSTALL_DATA) ./usr/lib/wrtgram/plugins/help/* $(1)/usr/lib/wrtgram/plugins/help/

	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins
	$(INSTALL_BIN) ./usr/lib/wrtgram/plugins/fw* \
				./usr/lib/wrtgram/plugins/get* \
				./usr/lib/wrtgram/plugins/hst* \
				./usr/lib/wrtgram/plugins/ignoredmac* \
				./usr/lib/wrtgram/plugins/interface* \
				./usr/lib/wrtgram/plugins/lan_scan \
				./usr/lib/wrtgram/plugins/netstat \
				./usr/lib/wrtgram/plugins/opkg* \
				./usr/lib/wrtgram/plugins/proc* \
				./usr/lib/wrtgram/plugins/reboot \
				./usr/lib/wrtgram/plugins/start \
				./usr/lib/wrtgram/plugins/status \
				./usr/lib/wrtgram/plugins/swports_list \
				./usr/lib/wrtgram/plugins/tmate \
				./usr/lib/wrtgram/plugins/wifi* \
				./usr/lib/wrtgram/plugins/wll_list \
				./usr/lib/wrtgram/plugins/cf_tunnel* \
		$(1)/usr/lib/wrtgram/plugins

	$(INSTALL_DIR) $(1)/sbin
	$(INSTALL_BIN) ./sbin/bot.py \
				./sbin/hosts_scan.py \
				./sbin/lanports.py \
		$(1)/sbin/
endef

define Package/wrtgram/postinst
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
	/etc/init.d/telegram_bot enable
	/etc/init.d/lanports enable
	/etc/init.d/hosts_scan enable
	/etc/init.d/telegram_bot start
	/etc/init.d/lanports start
	/etc/init.d/hosts_scan start
fi
exit 0
endef

define Package/wrtgram/prerm
#!/bin/sh
if [ -n "$${IPKG_INSTROOT}" ]; then
	/etc/init.d/telegram_bot stop
	/etc/init.d/lanports stop
	/etc/init.d/hosts_scan stop
	/etc/init.d/telegram_bot disable
	/etc/init.d/lanports disable
	/etc/init.d/hosts_scan disable
fi
exit 0
endef

$(eval $(call BuildPackage,wrtgram))
