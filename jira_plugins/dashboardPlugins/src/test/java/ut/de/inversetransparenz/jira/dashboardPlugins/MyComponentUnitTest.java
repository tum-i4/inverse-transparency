package ut.de.inversetransparenz.jira.dashboardPlugins;

import org.junit.Test;
import de.inversetransparenz.jira.dashboardPlugins.api.MyPluginComponent;
import de.inversetransparenz.jira.dashboardPlugins.impl.MyPluginComponentImpl;

import static org.junit.Assert.assertEquals;

public class MyComponentUnitTest
{
    @Test
    public void testMyName()
    {
        MyPluginComponent component = new MyPluginComponentImpl(null);
        assertEquals("names do not match!", "myComponent",component.getName());
    }
}