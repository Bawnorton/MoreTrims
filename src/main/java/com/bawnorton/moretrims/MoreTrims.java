package com.bawnorton.moretrims;

import net.fabricmc.api.ModInitializer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MoreTrims implements ModInitializer {
	public static final String MOD_ID = "moretrims";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	@Override
	public void onInitialize() {
		LOGGER.info("Initializing More Trims");
	}
}